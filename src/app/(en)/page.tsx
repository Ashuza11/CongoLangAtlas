import type { Metadata } from "next";
import AtlasExplorer from "@/components/atlas-explorer";

export const metadata: Metadata = {
  alternates: { languages: { en: "/", fr: "/fr" } },
};

export default function Home() {
  return <AtlasExplorer locale="en" />;
}
