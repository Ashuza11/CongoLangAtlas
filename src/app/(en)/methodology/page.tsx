import type { Metadata } from "next";
import MethodologyContent from "@/components/methodology-content";

export const metadata: Metadata = {
  title: "Methodology & contributions | CongoLangAtlas",
  description: "How CongoLangAtlas sources, reviews, maps, and publishes evidence, and how to contribute corrections, resources, or code.",
  alternates: { languages: { en: "/methodology", fr: "/fr/methodology" } },
};

export default function MethodologyPage() {
  return <MethodologyContent locale="en" />;
}
