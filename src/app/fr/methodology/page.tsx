import type { Metadata } from "next";
import MethodologyContent from "@/components/methodology-content";

export const metadata: Metadata = {
  title: "Méthodologie et contributions | CongoLangAtlas",
  description: "Découvrez comment CongoLangAtlas source, vérifie, cartographie et publie les données, et comment proposer une correction ou une ressource.",
  alternates: { languages: { en: "/methodology", fr: "/fr/methodology" } },
};

export default function FrenchMethodologyPage() {
  return <MethodologyContent locale="fr" />;
}
