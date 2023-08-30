package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"path"
)

type FeedTypes struct {
	All []string `json:"all"`
}

func ParseFeedTypes(file string) (*FeedTypes, error) {
	f, err := os.Open(file)
	if err != nil {
		return nil, err
	}
	defer f.Close()
	var ftypes FeedTypes
	err = json.NewDecoder(f).Decode(&ftypes)
	if err != nil {
		return nil, err
	}
	if len(ftypes.All) == 0 {
		return nil, fmt.Errorf("Feedtypes file %s has no 'all' field", file)
	}
	return &ftypes, nil
}

type Config struct {
	RootDir      string
	DataDir      string
	DatabaseUri  string
	BearerSecret string
	FeedTypes    *FeedTypes
	SQLEcho      bool
	Port         int
	LogRequests  bool
}

func ParseConfig() *Config {
	dbName := os.Getenv("FEED_DB_NAME")
	if dbName == "" {
		dbName = "feeddata.sqlite"
	}

	ftypesFile := os.Getenv("FEEDTYPES_FILE_NAME")
	if ftypesFile == "" {
		ftypesFile = "feedtypes.json"
	}

	var root string
	var dbpath string
	var dburi string
	var echo bool
	var port int
	var logrequests bool
	var datadir string

	flag.StringVar(&root, "root-dir", RootDir, "Root dir for backend (where Pipfile lives)")
	flag.StringVar(&datadir, "data-dir", path.Join(RootDir, "data"), "Data directory for JSON files")
	flag.StringVar(&dbpath, "db-path", path.Join(RootDir, dbName), "Path to sqlite database file")
	flag.StringVar(&dburi, "db-uri", "", "Database URI (overrides db-path)")
	flag.BoolVar(&logrequests, "log-requests", false, "Log info from HTTP requests to stderr")
	flag.StringVar(&ftypesFile, "ftypes-file", path.Join(RootDir, ftypesFile), "Path to feedtypes.json file")
	flag.BoolVar(&echo, "echo", false, "Echo SQL queries")
	flag.IntVar(&port, "port", 5100, "Port to listen on")

	flag.Parse()

	if dburi == "" {
		dburi = "file:" + dbpath + "?cache=shared&mode=rwc&_journal_mode=WAL"
	}

	if _, err := os.Stat(ftypesFile); os.IsNotExist(err) {
		log.Fatalf("Feedtypes file %s does not exist", ftypesFile)
	}

	secret := os.Getenv("BEARER_SECRET")
	if secret == "" {
		log.Fatal("BEARER_SECRET environment variable not set. This is required to authenticate the check/recheck endpoints.")
	}

	ftypes, err := ParseFeedTypes(path.Join(RootDir, "feedtypes.json"))
	if err != nil {
		log.Fatal(err)
	}

	return &Config{
		RootDir:      root,
		DatabaseUri:  dburi,
		BearerSecret: secret,
		FeedTypes:    ftypes,
		SQLEcho:      echo,
		LogRequests:  logrequests,
		Port:         port,
		DataDir:      datadir,
	}
}
