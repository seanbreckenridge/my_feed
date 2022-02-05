import Image from "./Image";
import styles from "../styles/Index.module.css";
import React, { useEffect, useRef, useState } from "react";
import {
  faBook,
  faChessKnight,
  faFilm,
  faGamepad,
  faMusic,
  faRecordVinyl,
  faVideo,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";

export type FeedItemStruct = {
  model_id: string;
  ftype: string;
  title: string;
  score: number | null;
  subtitle: string | null;
  creator: string | null;
  part: number | null;
  subpart: number | null;
  collection: string | null;
  when: string;
  release_date: string;
  image_url: string | null;
  url: string | null;
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

interface CardFooterProps {
  dt: string;
  score?: number | null;
}

const CardFooter: React.FC<CardFooterProps> = React.memo(
  ({ dt, score }: CardFooterProps) => {
    const sc = score ?? null;
    return (
      <div className={styles.cardFooter}>
        <div>{dt}</div>
        {score && <div className={styles.footerScore}>{`${sc}/10`}</div>}
      </div>
    );
  }
);

CardFooter.displayName = "Card Footer";

type CardImageProps = {
  src: string | null;
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
  if (!src) {
    return <></>;
  }
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
          <CardFooter dt={item.when} />
        </div>
      );
    } else if (item.ftype === "game_achievement") {
      let game_ach_title = item.title;
      if (item.model_id.startsWith("osrs_")) {
        game_ach_title = `OSRS - ${game_ach_title}`;
      }
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon className={styles.iconPadding} icon={faGamepad} />
            {game_ach_title}
          </p>
          <CardImage src={item.image_url} alt={item.title} />
          <p className={styles.subtitle}>{item.subtitle}</p>
          <CardFooter dt={item.when} />
        </div>
      );
    } else if (item.ftype === "game") {
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon className={styles.iconPadding} icon={faGamepad} />
            {item.title}
          </p>
          <CardImage src={item.image_url} alt={item.title} />
          <p className={styles.subtitle}>{item.subtitle}</p>
          <CardFooter dt={item.when} score={item.score} />
        </div>
      );
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
          <CardFooter dt={item.when} />
        </div>
      );
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
      const sc = item.ftype.includes("history") ? null : item.score;
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon className={styles.iconPadding} icon={faFilm} />
            {item.title}
          </p>
          <CardImage src={item.image_url} alt={item.title} />
          <p className={styles.subtitle}>{item.subtitle}</p>
          {seasonData.length ? (
            <p className={styles.subtitle}>{seasonData}</p>
          ) : null}
          <CardFooter dt={item.when} score={sc} />
        </div>
      );
    } else if (item.ftype === "album") {
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon
              className={styles.iconPadding}
              icon={faRecordVinyl}
            />
            {item.title}
          </p>
          <CardImage src={item.image_url} alt={item.title} />
          <p className={styles.subtitle}>{item.subtitle}</p>
          <CardFooter dt={item.when} score={item.score} />
        </div>
      );
    } else if (
      item.ftype === "anime_episode" ||
      item.ftype == "anime" ||
      item.ftype == "manga_chapter" ||
      item.ftype == "manga"
    ) {
      const sc =
        item.ftype == "anime" || item.ftype == "manga" ? item.score : null;
      const icon = item.ftype.startsWith("anime") ? faFilm : faBook;
      return (
        <div className={styles.cardFlexBody}>
          <p className={styles.title}>
            <FontAwesomeIcon className={styles.iconPadding} icon={icon} />
            {item.subtitle}
          </p>
          <CardImage src={item.image_url} alt={item.title} minHeight="25" />
          <p className={styles.subtitle}>{item.title}</p>
          <CardFooter dt={item.when} score={sc} />
        </div>
      );
    } else {
      console.log("Unknown type in switch", item);
      return <div>{`Unknown type in switch: ${item.ftype}`}</div>;
    }
  }
);

FeedBody.displayName = "FeedItem";
