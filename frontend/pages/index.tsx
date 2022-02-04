import type { GetStaticPropsResult, NextPage } from "next";
import Head from "next/head";
import Image from "../components/Image";
import { FeedGrid } from "../components/FeedItem";
import Select, { Options } from "react-select";
import styles from "../styles/Index.module.css";
import useSWRInfinite from "swr/infinite";
import { useState, useRef, useEffect, SetStateAction, Dispatch } from "react";
import { DebounceInput } from "react-debounce-input";

import useOnScreen from "../hooks/useOnScreen";
import { FeedItemOptions, OrderByOptions } from "../lib/enums";

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
    console.log(qt);
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
  const ref = useRef(null);
  const isVisible = useOnScreen(ref);

  const [queryText, setQueryText] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<string[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<string>(
    defaultSelectedOrder.value
  );

  // hit the end of the data for this query
  const [atEnd, setAtEnd] = useState<boolean>(false);

  const { data, error, mutate, size, setSize, isValidating } = useSWRInfinite(
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
        <div className={styles.filter_bar}>
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
        <FeedGrid data={feedItems} />
        <div ref={ref}>
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
