#GGEN - POP Terrain Generator for TouchDesigner
#Version 0.266
![GGEN System Overview](Assets/System/GGen_alpha.png)

**GGEN** aka (Gégène) is a modular POP (point operator) based procedural terrain generation toolkit for TouchDesigner that lets you build and iterate on believable landscapes by chaining 3D and 2D operators (noise, shape, terraces, erosion, cavities, slope, snow, beaches, etc.).

It can generate unlimited splatmaps stored as point attributes, tile and fill large 3D textures, and auto‑synthesize a powerful GLSL shader supporting height blending, and partial normal derivative for natural material transitions.

It provides separate terrain and splatmap networks for geometry shaping and texture/biome distribution, encourages a fully procedural, GPU‑friendly, non‑destructive workflow, and ships as reusable components you can extend, with contributions welcomed under the MIT license.

For more information, visit the [GGEN Wiki](https://github.com/CraftKontrol/GroundGen/wiki).

---

### Features

- **Modular Workflow:** Build complex terrains using a non destructive POP workflows with 3D and 2D operators.
- **Infinite Splatmaps:** Store splatmaps as point attributes as your grahic card can handle them.
- **3d Textures:** 3D texture filler system for managing large textures efficiently.
- **GLSL Shader Generation:** On-the-fly shader creation with blending parameters.
- **Advanced Blending:** Supports Partial Normal Derivatives and height blending for natural transitions.
- **Custom Nodes:** Includes pre-built TouchDesigner components to streamline your workflow.

---

## [Common-Networks](https://github.com/CraftKontrol/GroundGen/wiki/Common-Networks)

These are network zones where terrain and splatmap networks are built. They are managed and monitored continuously to update parameters and the shader in real time.

| Network | Description |
|---|---|
| [Terrain Network](https://github.com/CraftKontrol/GroundGen/wiki/Terrain-Network) | Constructs and manipulates terrain geometry: shape, elevation, large-scale forms, and physical features. |
| [Splatmap Network](https://github.com/CraftKontrol/GroundGen/wiki/Splatmap-Network) | Generates and blends splatmaps controlling texture/biome distribution across the terrain. |

---

## Node Operators

Node operators are the building blocks of your terrain and splatmap networks. They define how data flows and is processed within the system. They can be used to create complex interactions and effects by combining multiple operators.

## 3D Operators

| Operator | Purpose | Notes |
|---|---:|---|
| [Noise](https://github.com/CraftKontrol/GroundGen/wiki/Noise) | Add Perlin noise | Useful for fractal detail and turbulence. |
| [Shape](https://github.com/CraftKontrol/GroundGen/wiki/Shape) | Define base terrain forms | Uses profiles/curves for silhouette control. |
| [Terrace](https://github.com/CraftKontrol/GroundGen/wiki/Terrace) | Apply stepped terraces | Simulates plateaus, geological terraces. |
| [Erosion](https://github.com/CraftKontrol/GroundGen/wiki/Erosion) | Simulate hydraulic/thermal erosion | Carves slopes and sediment deposits. |
| [Beach](https://github.com/CraftKontrol/GroundGen/wiki/Beach) | Create coastline transitions | Blends sand and water edges at elevation ranges. |
| [Snow](https://github.com/CraftKontrol/GroundGen/wiki/Snow) | Altitude/slope-based snow coverage | Controls accumulation by slope. |

### 2D Operators

| Operator | Purpose | Notes |
|---|---:|---|
| [Cavity](https://github.com/CraftKontrol/GroundGen/wiki/Cavity) | Detect cavities/depressions | 2D Occlusion analysis. |
| [HeightMap](https://github.com/CraftKontrol/GroundGen/wiki/HeightMap) | Extract 2D heightmap from terrain flow | For export or downstream 2D processing. |
| [Level](https://github.com/CraftKontrol/GroundGen/wiki/Level) | Normalize/adjust texture values | Fit height or texture within specified bounds. |
| [Slope](https://github.com/CraftKontrol/GroundGen/wiki/Slope) | Compute terrain slope | Drive slope-based texturing or visualizations. |
| [Combiner](https://github.com/CraftKontrol/GroundGen/wiki/Combiner) | Blend multiple inputs | Useful for creating complex materials. |
| [Splatmap](https://github.com/CraftKontrol/GroundGen/wiki/Splatmap) | Generate splatmaps from point attributes | Controls texture/biome distribution for shaders. |
---


### Output Operators

| Operator | Purpose | Notes |
|---|---:|---|
| [GeoOut](https://github.com/CraftKontrol/GroundGen/wiki/GeoOut) | Outputs the final terrain geometry as a 3D model.                                   | Everywhere       |
| [MatOut](https://github.com/CraftKontrol/GroundGen/wiki/MatOut) | Outputs the final shader for the terrain.                                          | Everywhere      |
| [SplatOut](https://github.com/CraftKontrol/GroundGen/wiki/SplatOut) | Outputs the final splatmap in a TOP format.                                         | Everywhere      |

### TO DO maybe...

| Operator | Purpose | Notes |
|---|---:|---|
| Blender | Attribute mixer for splatmap networks | Combine and blend point attributes. |
| Thermal Wither | Simulate weathering effects | Models wind-driven material loss. |
| Splat Exporters | Export splatmaps for external engines | Includes Unreal, Unity, and other common formats. |
| Geometry Exporter | Export terrain geometry to external formats | Supports OBJ, FBX, and other common 3D formats. |
---


## Getting Started

1. **Clone the Repository.**

2. **Drag and drop the GGEN tox file everywhere into your TouchDesigner project.**

3. **Open the opMenu and browse operators in the GGen tab.**

4. **Click on the UI button to open the GroundGen interface.**

5. **Click on the "Open Terrain" button to open the Terrain Network.**

6. **Open the opMenu and create a GGen noise operator, and a GGen erosion operator.**

7. **Connect the noise operator to the erosion operator, and then connect the erosion operator to the output.**

8. **Click on the "Open Splatmaps" button to open the Splatmap Network.**

9. **Open the opMenu and create a GGen splatmap operator.**

10. **Connect the input to the splatmap operator.**

11. **Choose the erosion parameter from the source dropdown menu.**

12. **If not given, enter a name for the splatmap, e.g. "Erosion."**

13. **Once a splatmap is created, the shader will automatically update to include it.**

14. **Have Fun!**


## Documentation

For detailed documentation on how to use GGEN, please refer to the [wiki](https://github.com/CraftKontrol/GroundGen/wiki).

## Contributing

Contributions are welcome! Please submit issues or pull requests to help improve GGEN.

---

## Credits

##### Main & lone dev : Arnaud Cassone aka [Artcraft](https://www.artcraft-zone.com)
##### Thanks to derivative [TouchDesigner](https://derivative.ca/)
##### Thanks to [dotSimulate](https://www.dotsimulate.com/) and [tekt](https://www.patreon.com/posts/raytk-t3d-109418194) for the node family injector.
---

## License

MIT License. See [LICENSE](LICENSE) for details.