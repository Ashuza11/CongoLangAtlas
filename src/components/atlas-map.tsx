"use client";

import { useEffect, useRef } from "react";
import * as maplibregl from "maplibre-gl";
import type { Map as MapLibreMap, MapMouseEvent } from "maplibre-gl";
import type { AtlasPlaceSelection } from "@/lib/types";

interface AtlasMapProps {
  detailLevel: "provinces" | "territories";
  onPlaceSelect: (place: AtlasPlaceSelection) => void;
}

const EMPTY_STYLE: maplibregl.StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: "background", type: "background", paint: { "background-color": "#ede7da" } }],
};

export default function AtlasMap({ detailLevel, onPlaceSelect }: AtlasMapProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const detailRef = useRef(detailLevel);

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
          "fill-color": ["case", ["boolean", ["feature-state", "selected"], false], "#d96f43", "#c9d7c7"],
          "fill-opacity": ["case", ["boolean", ["feature-state", "selected"], false], 0.72, 0.78],
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
          "fill-color": ["case", ["boolean", ["feature-state", "selected"], false], "#d96f43", "#f1cf87"],
          "fill-opacity": ["case", ["boolean", ["feature-state", "selected"], false], 0.7, 0.28],
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

    const selectedIds: Record<"provinces" | "territories", string | number | undefined> = {
      provinces: undefined,
      territories: undefined,
    };
    const selectPlace = (event: MapMouseEvent) => {
      const layer = detailRef.current === "territories" ? "territory-fill" : "province-fill";
      const source = detailRef.current === "territories" ? "territories" : "provinces";
      const feature = map.queryRenderedFeatures(event.point, { layers: [layer] })[0];
      if (!feature) return;
      if (selectedIds[source] !== undefined) {
        map.setFeatureState({ source, id: selectedIds[source] }, { selected: false });
      }
      selectedIds[source] = feature.id;
      if (selectedIds[source] !== undefined) {
        map.setFeatureState({ source, id: selectedIds[source] }, { selected: true });
      }
      onPlaceSelect({
        id: `place-${String(feature.properties?.id ?? feature.id ?? "unknown")}`,
        name: String(feature.properties?.name ?? "Unknown place"),
        adminLevel: detailRef.current === "territories" ? "territory" : "province",
        parentId: feature.properties?.parent_id ? String(feature.properties.parent_id) : undefined,
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
