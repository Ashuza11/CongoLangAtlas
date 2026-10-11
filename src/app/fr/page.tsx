import type { Metadata } from "next";
import AtlasExplorer from "@/components/atlas-explorer";

export const metadata: Metadata = {
  title: "CongoLangAtlas — Ressources linguistiques documentées",
  description: "Explorez des métadonnées vérifiées sur les langues et ressources linguistiques liées à la République démocratique du Congo.",
  alternates: { languages: { en: "/", fr: "/fr" } },
};

export default function FrenchHome() {
  return <AtlasExplorer locale="fr" />;
}
