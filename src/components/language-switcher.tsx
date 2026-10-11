import Link from "next/link";
import type { Locale } from "@/lib/i18n";

export default function LanguageSwitcher({ locale, page = "atlas" }: { locale: Locale; page?: "atlas" | "methodology" }) {
  const englishHref = page === "methodology" ? "/methodology" : "/";
  const frenchHref = page === "methodology" ? "/fr/methodology" : "/fr";
  return (
    <nav className="language-switcher" aria-label={locale === "fr" ? "Choisir la langue" : "Choose language"}>
      <Link href={englishHref} hrefLang="en" lang="en" aria-current={locale === "en" ? "page" : undefined}>EN</Link>
      <Link href={frenchHref} hrefLang="fr" lang="fr" aria-current={locale === "fr" ? "page" : undefined}>FR</Link>
    </nav>
  );
}
