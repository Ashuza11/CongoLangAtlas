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

  useEffect(() => {
    highlightsRef.current = { provinces: highlightedProvinceIds, territories: highlightedTerritoryIds, selectedPlaceId };
    const map = mapRef.current;
    if (!map?.isStyleLoaded()) return;
    map.setPaintProperty("province-fill", "fill-color", fillExpression(highlightedProvinceIds, selectedPlaceId, "#c9d7c7"));
    map.setPaintProperty("territory-fill", "fill-color", fillExpression(highlightedTerritoryIds, selectedPlaceId, "#f1cf87"));
  }, [highlightedProvinceIds, highlightedTerritoryIds, selectedPlaceId]);

  useEffect(() => {
    detailRef.current = detailLevel;
    const map = mapRef.current;
    if (!map?.isStyleLoaded()) return;
    map.setLayoutProperty("territory-fill", "visibility", detailLevel === "territories" ? "visible" : "none");
    map.setLayoutProperty("territory-line", "visibility", detailLevel === "territories" ? "visible" : "none");
  }, [detailLevel]);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;
    maplibregl.setWorkerUrl("/maplibre/maplibre-gl-worker.mjs");
    const map = new maplibregl.Map({
      container: containerRef.current,
      style: EMPTY_STYLE,
      bounds: [[12.1, -13.7], [31.4, 5.5]],
      fitBoundsOptions: { padding: 42 },
      attributionControl: false,
    });
    mapRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    map.addControl(
      new maplibregl.AttributionControl({ customAttribution: "Administrative data: OCHA/RGC" }),
      "bottom-left",
    );

    map.on("load", () => {
      map.addSource("provinces", { type: "geojson", data: "/generated/geodata/cod-adm1.geojson", generateId: true });
      map.addSource("territories", { type: "geojson", data: "/generated/geodata/cod-adm2.geojson", generateId: true });
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
    });

    const selectPlace = (event: MapMouseEvent) => {
      const layer = detailRef.current === "territories" ? "territory-fill" : "province-fill";
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
    map.on("mousemove", (event: MapMouseEvent) => {
      const layers = [detailRef.current === "territories" ? "territory-fill" : "province-fill"];
      map.getCanvas().style.cursor = map.queryRenderedFeatures(event.point, { layers }).length ? "pointer" : "";
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, [onPlaceSelect]);

  return <div ref={containerRef} className="map-canvas" aria-label="Administrative map of the Democratic Republic of Congo" />;
}
