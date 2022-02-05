import type { NextPage } from "next";
import Head from "next/head";
import { FeedGrid, FeedItemStruct } from "../components/FeedItem";
import Select, { Options } from "react-select";
import styles from "../styles/Index.module.css";
import useSWRInfinite from "swr/infinite";
import {
  useState,
  useRef,
  useEffect,
  SetStateAction,
  Dispatch,
  ReactElement,
} from "react";
import { DebounceInput } from "react-debounce-input";

import useOnScreen from "../hooks/useOnScreen";
import { FeedItemOptions, OrderByOptions } from "../lib/enums";
import Link from "next/link";
import MyApp from "./_app";

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

const About: React.FC = () => {
  return (
    <div className={styles.about}>
      <p>{`A feed of media that I've seen`}</p>
      <a
        style={{ marginLeft: "20px" }}
        className={styles.link}
        href="https://github.com/seanbreckenridge/my_feed"
      >
        Source Code
      </a>
      <p>Any Images here are owned by the respective services:</p>
      <ul>
        <li>
          Scrobbles (Songs), using{" "}
          <a className={styles.link} href="https://listenbrainz.org/">
            ListenBrainz
          </a>
        </li>
        <li>
          Game Achievements from{" "}
          <a href="https://steamcommunity.com/" className={styles.link}>
            Steam
          </a>
        </li>
        <li>
          Album art from{" "}
          <a href="https://discogs.com/" className={styles.link}>
            Discogs
          </a>
        </li>
        <li>
          Anime/Manga from{" "}
          <a href="https://myanimelist.net/" className={styles.link}>
            MyAnimeList
          </a>
        </li>
        <li>
          Games from <a href="https://www.grouvee.com/">Grouvee</a>
        </li>
        <li>
          Movies/TV Shows/Episodes -{" "}
          <a className={styles.link} href="https://trakt.tv/">
            Trakt
          </a>
          , using{" "}
          <a className={styles.link} href="https://www.themoviedb.org/">
            TMDB
          </a>{" "}
          (This product uses the TMDB API but is not endorsed or certified by
          TMDB)
        </li>
      </ul>
    </div>
  );
};

interface IndexProps {}

const Index: NextPage<IndexProps> = ({}: IndexProps) => {
  const ref = useRef(null);
  const isVisible = useOnScreen(ref);

  const [showAttribution, setShowAttribution] = useState<boolean>(false);
  const [queryText, setQueryText] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<string>(
    defaultSelectedOrder.value
  );

  // hit the end of the data for this query
  const [atEnd, setAtEnd] = useState<boolean>(false);

  const { data, error, size, setSize, isValidating } = useSWRInfinite(
    (...args) =>
      getKey(
        ...args,
        dataBase,
        queryText,
        selectedTypes,
        selectedOrder,
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
    selectedOrder,
    selectedTypes,
    queryText,
  ]);

  // reset 'atEnd' (so new items load when you scroll down) after user changes any of the inputs
  useEffect(() => {
    setAtEnd(false);
  }, [queryText, selectedTypes, selectedOrder]);

  if (error) {
    return <div>{error}</div>;
  }

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
            <a href="#" onClick={() => setShowAttribution((toggle) => !toggle)}>
              About/Attribution
            </a>
          </div>
        </nav>
        {showAttribution && <About />}
        <div className={styles.filterBar}>
          <DebounceInput
            className={styles.query_input}
            value={queryText}
            minLength={2}
            debounceTimeout={300}
            onChange={(e) => setQueryText(e.target.value)}
            placeholder="Search..."
          />
          <Select
            defaultValue={[]}
            isMulti
            instanceId="type_select"
            inputId="type_select"
            options={FeedItemOptions}
            placeholder="Filter Type..."
            className={styles.type_select}
            onChange={(e) => setSelectedTypes(e.map((v) => (v as any).value))}
          />
          <Select
            defaultValue={defaultSelectedOrder}
            instanceId="score_select"
            inputId="score_select"
            options={OrderByOptions}
            className={styles.sort_select}
            onChange={(e) => e && setSelectedOrder(e.value)}
          />
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
        <div ref={ref} style={{ marginTop: "20vh" }}>
          {atEnd && selectedOrder === "score"
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
};

export default Index;
