import Image from "./Image";
import styles from "../styles/Index.module.css";
import React, { useEffect, useRef, useState } from "react";
import {
  faBook,
  faChessKnight,
  faFilm,
  faMusic,
  faVideo,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export type FeedItemStruct = {
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
  data: any;
};
interface FeedGridProps {
  data: FeedItemStruct[];
}

export const FeedGrid: React.FC<FeedGridProps> = ({ data }: FeedGridProps) => {
  return (
    <div className={styles.grid}>
      {data.map((feedItem: FeedItemStruct) => {
        return (
          <div key={feedItem.model_id}>
            <div className={styles.card}>
              <FeedBody item={feedItem} />
            </div>
          </div>
        );
      })}
    </div>
  );
};

interface TimestampProps {
  dt: string;
}

const Timestamp: React.FC<TimestampProps> = React.memo(
  ({ dt }: TimestampProps) => {
    return <div>{dt}</div>;
  }
);

Timestamp.displayName = "Timestamp";

type CardImageProps = {
  src: string;
  alt: string;
  minWidth?: string;
  minHeight?: string;
};

const CardImage: React.FC<CardImageProps> = ({
  src,
  alt,
  minWidth,
  minHeight,
}: CardImageProps) => {
  let uMinWidth = minWidth ?? "15";
  let uMinHeight = minHeight ?? "12";
  // hacky poster/still query params set in trakt
  if (src.endsWith("?p")) {
    uMinHeight = "30";
    src = src.slice(0, src.length - 2);
  } else if (src.endsWith("?s")) {
    uMinWidth = "20";
    src = src.slice(0, src.length - 2);
  }

  return (
    <div
      style={{
        minWidth: `${uMinWidth}rem`,
        minHeight: `${uMinHeight}rem`,
        width: "100%",
        height: "100%",
        position: "relative",
      }}
    >
      <Image
        src={src}
        alt={alt}
        layout="fill"
        objectFit="contain"
        unoptimized
      />
    </div>
  );
};

const padPart = (part: number): string => {
  return String(part).padStart(2, "0");
};

interface FeedBodyProps {
  item: FeedItemStruct;
}

export const FeedBody: React.FC<FeedBodyProps> = React.memo(
  ({ item }: FeedBodyProps) => {
    if (item.ftype === "scrobble") {
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon className={styles.iconPadding} icon={faMusic} />
            {item.title}
          </p>
          <p className={styles.subtitle}>{item.creator}</p>
          <p className={styles.subtitle}>{item.subtitle}</p>
          <Timestamp dt={item.when} />
        </div>
      );
    } else if (item.ftype === "game_achievement") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "game") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (item.ftype === "chess") {
      const svg = item.data.svg;
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon
              className={styles.iconPadding}
              icon={faChessKnight}
            />
            {item.title}
          </p>
          <div
            className={styles.chessSvg}
            dangerouslySetInnerHTML={{ __html: svg }}
          ></div>
          <p className={styles.subtitle}>{item.subtitle}</p>
          <Timestamp dt={item.when} />
        </div>
      );
      return <div>{JSON.stringify(item)}</div>;
    } else if (
      item.ftype === "trakt_history_episode" ||
      item.ftype == "trakt_history_movie" ||
      item.ftype == "trakt_show" ||
      item.ftype == "trakt_movie"
    ) {
      let seasonData = "";
      if (item.part && item.subpart) {
        seasonData = `S${padPart(item.part)}E${padPart(item.subpart)}`;
      }
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon className={styles.iconPadding} icon={faFilm} />
            {item.title}
          </p>
          {item.image_url !== null ? (
            <CardImage src={item.image_url} alt={item.title} />
          ) : null}
          <p className={styles.subtitle}>{item.subtitle}</p>
          {seasonData.length ? (
            <p className={styles.subtitle}>{seasonData}</p>
          ) : null}
          <Timestamp dt={item.when} />
        </div>
      );
    } else if (item.ftype === "album") {
      return <div>{JSON.stringify(item)}</div>;
    } else if (
      item.ftype === "anime_episode" ||
      item.ftype == "anime" ||
      item.ftype == "manga_chapter" ||
      item.ftype == "manga"
    ) {
      const icon = item.ftype.startsWith("anime") ? faFilm : faBook;
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon className={styles.iconPadding} icon={icon} />
            {item.subtitle}
          </p>
          {item.image_url !== null ? (
            <CardImage src={item.image_url} alt={item.title} />
          ) : null}
          <p className={styles.subtitle}>{item.title}</p>
          <Timestamp dt={item.when} />
        </div>
      );
    } else {
      console.log("Unknown type in switch", item);
      return <div>{`Unknown type in switch: ${item.ftype}`}</div>;
    }
  }
);

FeedBody.displayName = "FeedItem";
