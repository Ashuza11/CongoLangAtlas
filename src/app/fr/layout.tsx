import type { Metadata } from "next";
import "maplibre-gl/dist/maplibre-gl.css";
import "../globals.css";

export const metadata: Metadata = {
  title: "CongoLangAtlas — Ressources linguistiques documentées",
  description: "Explorez des métadonnées vérifiées sur les langues et ressources linguistiques liées à la République démocratique du Congo.",
};

export default function FrenchRootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="fr"><body>{children}</body></html>;
}
