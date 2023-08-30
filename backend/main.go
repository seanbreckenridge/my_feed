package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	_ "github.com/mattn/go-sqlite3"
	"log"
	"net/http"
	"net/url"
	"strconv"
	"strings"
)

var RootDir string

func auth(w *http.ResponseWriter, r *http.Request, bearerSecret string) bool {
	bearer := r.Header.Get("token")
	if bearer == "" {
		http.Error(*w, "token header missing", http.StatusUnauthorized)
		return false
	}
	if bearer != bearerSecret {
		http.Error(*w, "Invalid bearer token", http.StatusUnauthorized)
		return false
	}
	return true
}

type OrderBy string

const (
	When    OrderBy = "when"
	Score           = "score"
	Release         = "release"
)

type Sort string

const (
	Ascending  Sort = "asc"
	Descending      = "desc"
)

func parseEnumQueryParam(name string, query *url.Values, defaultValue string, allowed []string) (string, error) {
	val := query.Get(name)
	if val == "" {
		return defaultValue, nil
	}
	if contains(allowed, val) {
		return val, nil
	}
	return "", fmt.Errorf("Invalid %s: %s", name, val)
}

func parseIntegerQueryParam(name string, query *url.Values, defaultValue int, min int, max *int) (int, error) {
	val := query.Get(name)
	if val == "" {
		return defaultValue, nil
	}
	i, err := strconv.Atoi(val)
	if err != nil {
		return 0, fmt.Errorf("Invalid %s: %s", name, val)
	}
	return clamp(min, max, i), nil
}

var maxLimit int = 500

type checkResponse struct {
	Count int     `json:"added"`
	Error *string `json:"error"`
}

func main() {
	config := ParseConfig()

	var db *sql.DB
	var err error

	db, err = sql.Open("sqlite3", config.DatabaseUri)
	if err != nil {
		log.Fatal(err)
	}
	defer func() {
		err := db.Close()
		if err != nil {
			log.Fatal(err)
		}
	}()

	// initialize the database
	initDb(db)
	updateDatabaseFromJsonFiles(db, config)

	// Get the feed data
	count := rowCount(db)
	log.Printf("feedmodel table contains %d rows\n", count)

	// Start the web server
	http.HandleFunc("/check", func(w http.ResponseWriter, r *http.Request) {
		if !auth(&w, r, config.BearerSecret) {
			return
		}
		if config.LogRequests {
			log.Println("Running check...")
		}

		added, err := updateDatabaseFromJsonFiles(db, config)
		log.Printf("Added %d new items\n", added)
		checkResponse := checkResponse{Count: added}
		if err != nil {
			errString := err.Error()
			checkResponse.Error = &errString
		}
		json.NewEncoder(w).Encode(checkResponse)
	})
	http.HandleFunc("/recheck", func(w http.ResponseWriter, r *http.Request) {
		if !auth(&w, r, config.BearerSecret) {
			return
		}
		if config.LogRequests {
			log.Println("Running recheck...")
		}

		affected, err := clearDatabase(db)
		log.Printf("Cleared %d items\n", affected)
		if err != nil {
			log.Fatal(err)
		}
		count := rowCount(db)
		log.Printf("feedmodel table contains %d rows\n", count)
		added, err := updateDatabaseFromJsonFiles(db, config)
		log.Printf("Added %d new items\n", added)
		checkResponse := checkResponse{Count: added}
		if err != nil {
			errString := err.Error()
			checkResponse.Error = &errString
		}
		json.NewEncoder(w).Encode(checkResponse)
	})

	http.HandleFunc("/clear-data-dir", func(w http.ResponseWriter, r *http.Request) {
		if !auth(&w, r, config.BearerSecret) {
			return
		}
		if config.LogRequests {
			log.Println("Clearing data dir...")
		}
		err := clearDataDir(config)
		if err != nil {
			// write back to user
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(err.Error()))
			log.Fatal(err)
		} else {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("Data dir cleared\n"))
		}
	})

	http.HandleFunc("/data/ids", func(w http.ResponseWriter, r *http.Request) {
		ids := modelIds(db)
		if config.LogRequests {
			log.Printf("Found %d ids\n", len(ids))
		}
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(ids)
	})

	http.HandleFunc("/data/types", func(w http.ResponseWriter, r *http.Request) {
		types := feedTypes(db)
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(types)
	})

	http.HandleFunc("/data/", func(w http.ResponseWriter, r *http.Request) {

		// parse query params
		qrParams := r.URL.Query()
		offset, err := parseIntegerQueryParam("offset", &qrParams, 0, 0, nil)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		limit, err := parseIntegerQueryParam("limit", &qrParams, 100, 1, &maxLimit)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		orderRaw, err := parseEnumQueryParam("order_by", &qrParams, string(When), []string{string(When), string(Score), string(Release)})
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		orderBy := OrderBy(orderRaw)

		sortRaw, err := parseEnumQueryParam("sort", &qrParams, string(Descending), []string{string(Ascending), string(Descending)})
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		sort := Sort(sortRaw)

		var filterFtypes []string
		ftypeRaw := qrParams.Get("ftype")
		if ftypeRaw != "" {
			if strings.Contains(ftypeRaw, ",") {
				filterFtypes = strings.Split(ftypeRaw, ",")
			} else {
				filterFtypes = []string{ftypeRaw}
			}
		}

		// validate to make sure all ftypes are valid
		for _, ftype := range filterFtypes {
			if !contains(config.FeedTypes.All, ftype) {
				http.Error(w, fmt.Sprintf("Invalid ftype value %s", ftype), http.StatusBadRequest)
				return
			}
		}

		query := r.URL.Query().Get("query")
		if strings.TrimSpace(query) == "" {
			query = ""
		}

		if config.LogRequests {
			log.Printf("Running data/ with offset '%d', limit '%d', orderBy '%s', sort '%s', ftype filter %+v, query '%s'\n", offset, limit, orderBy, sort, filterFtypes, query)
		}

		models, err := queryData(db, config, query, filterFtypes, orderBy, sort, limit, offset)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(models)
	})

	fmt.Printf("Starting server on port %d\n", config.Port)
	log.Fatal(http.ListenAndServe(fmt.Sprintf(":%d", config.Port), nil))
}
