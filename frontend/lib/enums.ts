export type LabelOption = {
  value: string;
  label: string;
};

function modelIdToLabel(key: string) {
  let buf = "";
  key.split("_").forEach((part: string) => {
    buf += part.charAt(0).toUpperCase();
    buf += part.slice(1);
    buf += " ";
  });
  return buf.trim();
}

function createOptions(ids: string[]): LabelOption[] {
  const opts: LabelOption[] = [];
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

export const FeedItemOptions: LabelOption[] = createOptions(
  // remove trakt_history_movie since filtering by that only shows things Ive rewatched, isnt that useful
  Array.from(FeedItemTypes)
    .filter((e) => e !== "trakt_history_movie")
    .sort((a, b) => (a < b ? -1 : 1))
);

export const OrderByOptions: LabelOption[] = [
  {
    value: "when",
    label: "Date",
  },
  {
    value: "score",
    label: "Score",
  },
];
