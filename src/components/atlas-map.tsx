"use client";

import { useEffect, useRef } from "react";
import * as maplibregl from "maplibre-gl";
import type { Map as MapLibreMap, MapMouseEvent } from "maplibre-gl";
import type { AtlasPlaceSelection } from "@/lib/types";

interface AtlasMapProps {
  detailLevel: "provinces" | "territories";
  highlightedProvinceIds: string[];
  highlightedTerritoryIds: string[];
  selectedPlaceId?: string;
  onPlaceSelect: (place: AtlasPlaceSelection) => void;
}

interface BoundaryFeatureCollection {
  features: Array<{
    properties?: { id?: string; name?: string };
    geometry?: { coordinates?: unknown };
  }>;
}

const COUNTRY_BOUNDS: [[number, number], [number, number]] = [[12.1, -13.7], [31.4, 5.5]];

const EMPTY_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: "background", type: "background", paint: { "background-color": "#ede7da" } }],
};

function geometryIds(placeIds: string[]) {
  return placeIds.map((id) => id.replace(/^place-/, ""));
}

function fillExpression(ids: string[], selectedPlaceId: string | undefined, baseColor: string): maplibregl.ExpressionSpecification {
  return [
    "case",
    ["==", ["get", "id"], selectedPlaceId?.replace(/^place-/, "") ?? ""], "#d96f43",
    ["in", ["get", "id"], ["literal", geometryIds(ids)]], "#356f66",
    baseColor,
  ];
}

function boundaryBounds(collection: BoundaryFeatureCollection | null, placeIds: string[]) {
  if (!collection || !placeIds.length) return null;
  const geometryIds = new Set(placeIds.map((id) => id.replace(/^place-/, "")));
  const bounds = new maplibregl.LngLatBounds();
  const extendCoordinates = (coordinates: unknown) => {
    if (!Array.isArray(coordinates)) return;
    if (coordinates.length >= 2 && typeof coordinates[0] === "number" && typeof coordinates[1] === "number") {
      bounds.extend([coordinates[0], coordinates[1]]);
      return;
    }
    coordinates.forEach(extendCoordinates);
  };
  collection.features
    .filter((feature) => feature.properties?.id && geometryIds.has(feature.properties.id))
    .forEach((feature) => extendCoordinates(feature.geometry?.coordinates));
  return bounds.isEmpty() ? null : bounds;
}

export default function AtlasMap({
  detailLevel,
  highlightedProvinceIds,
  highlightedTerritoryIds,
  selectedPlaceId,
  onPlaceSelect,
}: AtlasMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const detailRef = useRef(detailLevel);
  const highlightsRef = useRef({ provinces: highlightedProvinceIds, territories: highlightedTerritoryIds, selectedPlaceId });
  const boundariesRef = useRef<{ provinces: BoundaryFeatureCollection | null; territories: BoundaryFeatureCollection | null }>({ provinces: null, territories: null });

  useEffect(() => {
    highlightsRef.current = { provinces: highlightedProvinceIds, territories: highlightedTerritoryIds, selectedPlaceId };
    const map = mapRef.current;
    if (!map?.isStyleLoaded() || !map.getLayer("province-fill") || !map.getLayer("territory-fill")) return;
    map.setPaintProperty("province-fill", "fill-color", fillExpression(highlightedProvinceIds, selectedPlaceId, "#c9d7c7"));
    map.setPaintProperty("territory-fill", "fill-color", fillExpression(highlightedTerritoryIds, selectedPlaceId, "#f1cf87"));
    const selectedBounds = selectedPlaceId
      ? boundaryBounds(selectedPlaceId.includes("adm2") ? boundariesRef.current.territories : boundariesRef.current.provinces, [selectedPlaceId])
      : null;
    const evidenceBounds = selectedBounds
      ?? boundaryBounds(boundariesRef.current.provinces, highlightedProvinceIds)
      ?? boundaryBounds(boundariesRef.current.territories, highlightedTerritoryIds);
    if (evidenceBounds) map.fitBounds(evidenceBounds, { padding: 76, maxZoom: selectedPlaceId ? 7 : 5.8, duration: 650 });
    else if (!selectedPlaceId && !highlightedProvinceIds.length && !highlightedTerritoryIds.length) {
      map.fitBounds(COUNTRY_BOUNDS, { padding: 42, duration: 650 });
    }
  }, [highlightedProvinceIds, highlightedTerritoryIds, selectedPlaceId]);

  useEffect(() => {
    detailRef.current = detailLevel;
    const map = mapRef.current;
    if (!map?.isStyleLoaded() || !map.getLayer("territory-fill") || !map.getLayer("territory-line")) return;
    map.setLayoutProperty("territory-fill", "visibility", detailLevel === "territories" ? "visible" : "none");
    map.setLayoutProperty("territory-line", "visibility", detailLevel === "territories" ? "visible" : "none");
  }, [detailLevel]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    maplibregl.setWorkerUrl("/maplibre/maplibre-gl-worker.mjs");
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: EMPTY_STYLE,
      bounds: COUNTRY_BOUNDS,
      fitBoundsOptions: { padding: 42 },
      attributionControl: false,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    map.addControl(
      new maplibregl.AttributionControl({ customAttribution: "Administrative data: OCHA/RGC" }),
      "bottom-left",
    );

    map.on("load", async () => {
      const [provinces, territories] = await Promise.all([
        fetch("/generated/geodata/cod-adm1.geojson").then((response) => response.json() as Promise<BoundaryFeatureCollection>),
        fetch("/generated/geodata/cod-adm2.geojson").then((response) => response.json() as Promise<BoundaryFeatureCollection>),
      ]);
      if (mapRef.current !== map) return;
      boundariesRef.current = { provinces, territories };
      map.addSource("provinces", { type: "geojson", data: provinces as GeoJSON.FeatureCollection, generateId: true });
      map.addSource("territories", { type: "geojson", data: territories as GeoJSON.FeatureCollection, generateId: true });
      map.addLayer({
        id: "province-fill",
        type: "fill",
        source: "provinces",
        paint: {
          "fill-color": fillExpression(highlightsRef.current.provinces, highlightsRef.current.selectedPlaceId, "#c9d7c7"),
          "fill-opacity": 0.78,
        },
      });
      map.addLayer({
        id: "province-line",
        type: "line",
        source: "provinces",
        paint: { "line-color": "#173c35", "line-width": 1.2 },
      });
      map.addLayer({
        id: "territory-fill",
        type: "fill",
        source: "territories",
        layout: { visibility: detailRef.current === "territories" ? "visible" : "none" },
        paint: {
          "fill-color": fillExpression(highlightsRef.current.territories, highlightsRef.current.selectedPlaceId, "#f1cf87"),
          "fill-opacity": 0.28,
        },
      });
      map.addLayer({
        id: "territory-line",
        type: "line",
        source: "territories",
        layout: { visibility: detailRef.current === "territories" ? "visible" : "none" },
        paint: { "line-color": "#6d796d", "line-width": 0.65 },
      });
      const active = highlightsRef.current;
      const selectedBounds = active.selectedPlaceId
        ? boundaryBounds(active.selectedPlaceId.includes("adm2") ? territories : provinces, [active.selectedPlaceId])
        : null;
      const evidenceBounds = selectedBounds
        ?? boundaryBounds(provinces, active.provinces)
        ?? boundaryBounds(territories, active.territories);
      if (evidenceBounds) map.fitBounds(evidenceBounds, { padding: 76, maxZoom: active.selectedPlaceId ? 7 : 5.8, duration: 0 });
    });

    const selectPlace = (event: MapMouseEvent) => {
      const layer = detailRef.current === "territories" ? "territory-fill" : "province-fill";
      if (!map.getLayer(layer)) return;
      const feature = map.queryRenderedFeatures(event.point, { layers: [layer] })[0];
      if (!feature) return;
      onPlaceSelect({
        id: `place-${String(feature.properties?.id ?? feature.id ?? "unknown")}`,
        name: String(feature.properties?.name ?? "Unknown place"),
        adminLevel: detailRef.current === "territories" ? "territory" : "province",
        parentId: feature.properties?.parent_id ? `place-${String(feature.properties.parent_id)}` : undefined,
      });
    };
    map.on("click", selectPlace);
    const hoverPopup = new maplibregl.Popup({ closeButton: false, closeOnClick: false, offset: 12, className: "place-tooltip" });
    map.on("mousemove", (event: MapMouseEvent) => {
      const layer = detailRef.current === "territories" ? "territory-fill" : "province-fill";
      if (!map.getLayer(layer)) return;
      const feature = map.queryRenderedFeatures(event.point, { layers: [layer] })[0];
      map.getCanvas().style.cursor = feature ? "pointer" : "";
      if (feature) hoverPopup.setLngLat(event.lngLat).setText(String(feature.properties?.name ?? "Unknown place")).addTo(map);
      else hoverPopup.remove();
    });
    map.getCanvas().addEventListener("mouseleave", () => hoverPopup.remove());

    return () => {
      hoverPopup.remove();
      map.remove();
      mapRef.current = null;
    };
  }, [onPlaceSelect]);

  return <div ref={containerRef} className="map-canvas" aria-label="Administrative map of the Democratic Republic of Congo" />;
}
