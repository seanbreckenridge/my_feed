import Image from "./Image";
import styles from "../styles/Index.module.css";
import React from "react";

type FeedItemStruct = {
  model_id: string;
  ftype: string;
  title: string;
  score: string;
  subtitle: string;
  creator: string;
  part: number;
  subpart: number;
  collection: string;
  when: string;
  release_date: string;
  image_url: string;
  url: string;
  tags: string[];
  data: Object;
};
interface FeedGridProps {
  data: Object[];
}

export const FeedGrid: React.FC<FeedGridProps> = ({ data }: FeedGridProps) => {
  return (
    <div className={styles.grid}>
      {data.map((feedItem) => {
        return (
          <div key={(feedItem as FeedItemStruct).model_id}>
            <div className={styles.card}>
              <FeedBody item={feedItem as FeedItemStruct} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

interface FeedBodyProps {
  item: FeedItemStruct;
}

export const FeedBody: React.FC<FeedBodyProps> = React.memo(
  ({ item }: FeedBodyProps) => {
    if (item.ftype === "scrobble") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "game_achievement") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "game") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "chess") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "trakt_episode") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "trakt_movie") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "album") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "anime_episode") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "anime") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "manga_chapter") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "manga") {
      return <div>{JSON.stringify(item)}</div>;
    } else {
      console.log("Unknown type in switch", item);
      return <div>{`Unknown type in switch: ${item.ftype}`}</div>;
    }
  }
);
