function modelIdToLabel(key: string) {
  let buf = "";
  key.split("_").forEach((part: string) => {
    buf += part.charAt(0).toUpperCase();
    buf += part.slice(1);
    buf += " ";
  });
  return buf.trim();
}

function createOptions(ids: string[]): any[] {
  const opts: any[] = [];
  ids.forEach((uid: string) => {
    opts.push({
      value: uid,
      label: modelIdToLabel(uid),
    });
  });
  return opts;
}

export const FeedItemTypes: Set<string> = new Set<string>(
  require("../data/feed_types.json")
);

export const FeedItemOptions = createOptions(
  // remove trakt_history_movie since filtering by that only shows things Ive rewatched, isnt that useful
  Array.from(FeedItemTypes)
    .filter((e) => e !== "trakt_history_movie")
    .sort((a, b) => (a < b ? -1 : 1))
);

export const OrderByOptions = [
  {
    value: "when",
    label: "Date",
  },
  {
    value: "score",
    label: "Score",
  },
];
