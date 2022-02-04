import NextImage from "next/image";

interface ICustomLoader {
  src: string;
}

// opt-out of image optimization, no-op
const CustomLoader = ({src}: ICustomLoader) => src;

export default function Image(props: any) {
  return (
    <NextImage
      {...props}
      loader={CustomLoader}
    />
  );
}
