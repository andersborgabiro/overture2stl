(provided by GPT-4.1)

Overture Maps Foundation provides open map data in a set of standardized layers, each called a "map type." Here’s an explanation of the real-world meaning and content of each map type you listed, based on Overture’s documentation and general mapping concepts:

---

### 1. **address**
**Real-world meaning:**  
Represents specific locations where people can receive mail or packages, such as homes, businesses, or public buildings.

**Content:**  
- Street addresses (house/building number, street name, city, postal code, etc.)
- Geographical coordinates (latitude/longitude) for each address
- Address components (unit, floor, etc.)

---

### 2. **building**
**Real-world meaning:**  
Physical structures constructed for human use or occupancy.

**Content:**  
- Footprints (2D outlines) of buildings
- Building heights (sometimes)
- Building types (residential, commercial, etc.)
- Associated metadata (name, address, etc.)

---

### 3. **building_part**
**Real-world meaning:**  
Subdivisions of a building, representing different sections, wings, or floors.

**Content:**  
- 3D geometry or attributes for parts of a building (e.g., different heights, uses, or architectural features)
- Relationships to parent building

---

### 4. **division**
**Real-world meaning:**  
Administrative or political subdivisions, such as countries, states, provinces, counties, or municipalities.

**Content:**  
- Names and codes for each division
- Hierarchical relationships (e.g., city within a state)
- Reference to boundaries

---

### 5. **division_area**
**Real-world meaning:**  
The actual geographic area covered by an administrative division.

**Content:**  
- Polygon geometry representing the area of a division (e.g., the outline of a country or city)

---

### 6. **division_boundary**
**Real-world meaning:**  
The lines that define the limits between administrative divisions.

**Content:**  
- Line geometry for the borders between divisions (e.g., the border between two countries or states)

---

### 7. **places**
**Real-world meaning:**  
Named locations of interest, such as cities, towns, villages, neighborhoods, landmarks, or points of interest (POIs).

**Content:**  
- Place names and types (city, park, restaurant, etc.)
- Coordinates
- Additional attributes (population, importance, etc.)

---

### 8. **segment**
**Real-world meaning:**  
Individual sections of transportation networks, such as roads, railways, or paths.

**Content:**  
- Line geometry for each segment
- Attributes (road type, speed limit, direction, etc.)
- Connectivity information

---

### 9. **connector**
**Real-world meaning:**  
Special links that connect different segments in the transportation network, often representing intersections, ramps, or transitions.

**Content:**  
- Line or point geometry
- Information about how segments are connected (e.g., a ramp connecting a highway to a local road)

---

### 10. **bathymetry**
**Real-world meaning:**  
The measurement of the depth of water bodies (oceans, seas, lakes) and the shape of underwater terrain.

**Content:**  
- Depth values (below sea level)
- Underwater contours and features (e.g., trenches, ridges)

---

### 11. **infrastructure**
**Real-world meaning:**  
Man-made structures and facilities that support society, such as bridges, tunnels, power lines, pipelines, etc.

**Content:**  
- Geometry and attributes for infrastructure elements
- Types (bridge, tunnel, dam, etc.)

---

### 12. **land**
**Real-world meaning:**  
The physical surface of the Earth that is not covered by water.

**Content:**  
- Landmass outlines (continents, islands)
- May include elevation or terrain data

---

### 13. **land_cover**
**Real-world meaning:**  
The physical material at the surface of the earth, such as vegetation, urban areas, bare soil, or water.

**Content:**  
- Classification of surface types (forest, grassland, urban, etc.)
- Polygon geometry for each cover type

---

### 14. **land_use**
**Real-world meaning:**  
How humans use the land, such as for agriculture, residential, commercial, industrial, or recreational purposes.

**Content:**  
- Classification of land by use (farmland, park, industrial zone, etc.)
- Polygon geometry for each use area

---

### 15. **water**
**Real-world meaning:**  
Bodies of water on the Earth’s surface, such as oceans, lakes, rivers, and reservoirs.

**Content:**  
- Polygon and line geometry for water features
- Attributes (name, type, flow direction, etc.)

---

**Summary Table:**

| Map Type           | Real-World Content Example                      |
|--------------------|------------------------------------------------|
| address            | 123 Main St, Springfield                       |
| building           | Apartment block, office tower                  |
| building_part      | East wing, 3rd floor of a mall                 |
| division           | State of California, City of Paris             |
| division_area      | Polygon of California’s area                   |
| division_boundary  | Border line between France and Germany         |
| places             | Eiffel Tower, Central Park, Tokyo              |
| segment            | A stretch of highway, a railway section        |
| connector          | Highway on-ramp, intersection node             |
| bathymetry         | Depth of the Atlantic Ocean                    |
| infrastructure     | Golden Gate Bridge, Hoover Dam                 |
| land               | Outline of Africa, Greenland                   |
| land_cover         | Forest, urban area, desert                     |
| land_use           | Farmland, residential zone, industrial park    |
| water              | Lake Superior, Amazon River                    |

---

**References:**
- [Overture Maps Data Schema](https://docs.overturemaps.org/data-schemas/)
- [Overture Maps Documentation](https://docs.overturemaps.org/)
- General GIS and mapping knowledge

