import type { NextPage } from "next";
import Head from "next/head";
import { FeedGrid, FeedItemStruct } from "../components/FeedItem";
import Select from "react-select";
import styles from "../styles/Index.module.css";
import useSWRInfinite from "swr/infinite";
import { useState, useRef, useEffect, SetStateAction, Dispatch } from "react";
import { DebounceInput } from "react-debounce-input";
import { useQueryParam, StringParam, withDefault } from "next-query-params";
import useOnScreen from "../hooks/useOnScreen";
import { FeedItemOptions, LabelOption, OrderByOptions } from "../lib/enums";
import PrefsConsumer, { Prefs } from "../lib/prefs";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faClock, faHistory, faTimes } from "@fortawesome/free-solid-svg-icons";
import About from "../components/About";

async function fetcher(...args: any[]) {
  // @ts-ignore
  const res = await fetch(...args);
  return res.json();
}

const createQuery = (obj: any) => {
  let str = "";
  for (const key in obj) {
    if (str != "") {
      str += "&";
    }
    str += key + "=" + encodeURIComponent(obj[key]);
  }
  return str;
};

const getKey = (
  pageIndex: number,
  previousPageData: any,
  baseUrl: string,
  query: string,
  selectedTypes: string[],
  selectedOrder: string,
  limit: number,
  setAtEnd: Dispatch<SetStateAction<boolean>>
) => {
  if (previousPageData && !previousPageData.length) {
    setAtEnd(true);
    return null; // reached the end
  }

  let offset = 0;
  if (pageIndex > 0) {
    offset = pageIndex * 100;
  }

  let params: any = {
    offset: offset,
    limit: limit,
  };

  const qt = query.trim();
  if (qt.length > 0) {
    params.query = qt;
  }

  if (selectedOrder.length > 0) {
    params.order_by = selectedOrder;
    params.sort = "desc";
  }

  if (selectedTypes.length > 0) {
    params.ftype = selectedTypes.join(",");
  }

  return `${baseUrl}?${createQuery(params)}`;
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL;
if (!baseUrl) {
  throw new Error(`No base URL: ${baseUrl}`);
}

const dataBase = `${baseUrl}/data/`;
const paginationLimit = 100;
const defaultSelectedOrder = OrderByOptions[0];

interface IndexProps {}

const Index: NextPage<IndexProps> = ({}: IndexProps) => {
  const scrollRef = useRef(null);
  const isVisible = useOnScreen(scrollRef);

  const [showAttribution, setShowAttribution] = useState<boolean>(false);

  // query maps back onto the URL param
  const [queryText, setQueryText] = useQueryParam(
    "query",
    withDefault(StringParam, "")
  );

  // valid type labels, used in Select, sent to API
  const [selectedTypeLabels, setSelectedTypeLabels] = useState<LabelOption[]>(
    []
  );

  // valid order by, used in select and sent to API
  const [selectedOrderLabel, setSelectedOrderLabel] =
    useState<LabelOption>(defaultSelectedOrder);

  // hit the end of the data for this query
  const [atEnd, setAtEnd] = useState<boolean>(false);

  const { data, error, size, setSize, isValidating } = useSWRInfinite(
    (...args) =>
      getKey(
        ...args,
        dataBase,
        queryText,
        selectedTypeLabels.map((e) => e.value),
        selectedOrderLabel.value,
        paginationLimit,
        setAtEnd
      ),
    fetcher
  );

  const feedItems = data ? [].concat(...data) : [];
  const isLoadingInitialData = !data && !error;
  const isLoadingMore =
    isLoadingInitialData ||
    (size > 0 && data && typeof data[size - 1] === "undefined");
  const isEmpty = data?.[0]?.length === 0;
  const isRefreshing = isValidating && data && data.length === size;

  useEffect(() => {
    if (
      isVisible &&
      !atEnd &&
      !isRefreshing &&
      !isLoadingInitialData &&
      !isLoadingMore
    ) {
      setSize(size + 1);
    }
  }, [
    isVisible,
    isRefreshing,
    atEnd,
    isLoadingMore,
    selectedOrderLabel,
    selectedTypeLabels,
    queryText,
  ]);

  // reset 'atEnd' (so new items load when you scroll down) after user changes any of the inputs
  useEffect(() => {
    setAtEnd(false);
  }, [queryText, selectedOrderLabel, selectedTypeLabels]);

  const clear = () => {
    setQueryText("");
    setSelectedOrderLabel(defaultSelectedOrder);
    setSelectedTypeLabels([]);
    setSize(0);
  };

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <PrefsConsumer>
      {(prefs: Prefs) => {
        return (
          <div className={styles.container}>
            <Head>
              <title>media feed</title>
              <meta name="description" content="my personal media feed" />
              <link rel="icon" href="https://sean.fish/favicon.ico" />
            </Head>
            <main className={styles.main}>
              <nav className={styles.nav}>
                <div className={styles.mainTitle}>- FEED -</div>
                <div className={styles.mutedLink}>
                  <a
                    href="#"
                    onClick={() => setShowAttribution((toggle) => !toggle)}
                  >
                    About/Attribution
                  </a>
                </div>
              </nav>
              {showAttribution && <About />}
              <div className={styles.filterBar}>
                <DebounceInput
                  className={styles.queryInput}
                  value={queryText}
                  minLength={2}
                  aria-label="Search"
                  debounceTimeout={300}
                  onChange={(e) => setQueryText(e.target.value)}
                  placeholder="Search..."
                />
                <label>
                  <Select
                    value={selectedTypeLabels}
                    isMulti
                    instanceId="type_select"
                    inputId="type_select"
                    options={FeedItemOptions}
                    placeholder="Filter Type..."
                    aria-label="Filter Types"
                    className={styles.typeSelect}
                    onChange={(e) => {
                      if (e) {
                        setSelectedTypeLabels(e as LabelOption[]);
                      }
                    }}
                  />
                </label>
                <label>
                  <Select
                    value={selectedOrderLabel}
                    instanceId="order_select"
                    inputId="order_select"
                    aria-label="Select Order"
                    options={OrderByOptions}
                    className={styles.sortSelect}
                    onChange={(e) => {
                      if (e) {
                        setSelectedOrderLabel(e);
                      }
                    }}
                  />
                </label>
                <div
                  className={styles.filterIcon}
                  title="Toggle Date Format"
                  onClick={() => {
                    // toggle on click
                    prefs.setPrefs((oldPrefs: Prefs): Prefs => {
                      return {
                        ...oldPrefs,
                        dateAbsolute: !oldPrefs.dateAbsolute,
                      };
                    });
                  }}
                >
                  <FontAwesomeIcon
                    icon={prefs.dateAbsolute ? faClock : faHistory}
                  />
                </div>
                <div
                  className={styles.filterIcon}
                  title="Reset Filters"
                  onClick={clear}
                >
                  <FontAwesomeIcon icon={faTimes} />
                </div>
              </div>
              {/*
        <p>
          showing {size} page(s) of{" "}
          {isLoadingMore && !atEnd ? "..." : feedItems.length} items(s){" "}
        </p>
          <button
            onClick={() => {
              setQueryText(queryText);
              setSize(1);
            }}
          >
            Fetch
          </button>
          <button disabled={isRefreshing} onClick={() => mutate()}>
            {isRefreshing ? "refreshing..." : "refresh"}
          </button>
          <button disabled={!size} onClick={() => setSize(0)}>
            clear
          </button>
          {isEmpty ? <p>Nothing here...</p> : null}
        */}
              <FeedGrid data={feedItems as FeedItemStruct[]} />
              <div ref={scrollRef} style={{ marginTop: "20vh" }}>
                {atEnd && selectedOrderLabel.value === "score"
                  ? "no more data with scores, switch order to 'Date'"
                  : atEnd
                  ? "no more data..."
                  : !isEmpty && isLoadingMore
                  ? "loading..."
                  : ""}
              </div>
            </main>
          </div>
        );
      }}
    </PrefsConsumer>
  );
};

export default Index;
