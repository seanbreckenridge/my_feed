import type { NextPage } from "next";
import Head from "next/head";
import Image from "../components/Image";
import styles from "../styles/Index.module.css";
import useSWRInfinite from "swr/infinite";
import { useState, useRef, useEffect, SetStateAction, Dispatch } from "react";
import { DebounceInput } from "react-debounce-input";

import useOnScreen from "../hooks/useOnScreen";

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
    console.log(qt);
    params.query = qt;
  }

  return `${baseUrl}?${createQuery(params)}`;
};

const baseUrl = process.env.NEXT_PUBLIC_API_URL;
if (!baseUrl) {
  throw new Error(`No base URL: ${baseUrl}`);
}

const dataBase = `${baseUrl}/data/`;
const paginationLimit = 100;

const Index: NextPage = () => {
  const ref = useRef();
  const isVisible = useOnScreen(ref);

  const [queryText, setQueryText] = useState("");

  // hit the end of the data for this query
  const [atEnd, setAtEnd] = useState<boolean>(false);

  const { data, error, mutate, size, setSize, isValidating } = useSWRInfinite(
    (...args) =>
      getKey(...args, dataBase, queryText, paginationLimit, setAtEnd),
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
  }, [isVisible, isRefreshing, atEnd]);

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
        <DebounceInput
          value={queryText}
          minLength={2}
          debounceTimeout={300}
          onChange={(e) => setQueryText(e.target.value)}
          placeholder="..."
        />
        <p>
          showing {size} page(s) of{" "}
          {isLoadingMore && !atEnd ? "..." : feedItems.length} items(s){" "}
        </p>
        {/*
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
        <div className={styles.grid}>
          {feedItems.map((feedItem: any) => {
            return (
              <div key={feedItem.model_id} className={styles.card}>
                {JSON.stringify(feedItem)}
              </div>
            );
          })}
        </div>
        <div ref={ref as any}>
          {atEnd
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
