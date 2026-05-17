# Mini Program Assets

Place Figma-exported images, SVG/PNG icons, and illustrations here before final visual lock.

Current implementation keeps the image URLs from `src/app/components/petposter/tokens.ts`.

`assets/icons/` contains mini-program-safe SVG replacements for the React `lucide-react` icons used in the Figma export. These reduce text-placeholder drift, but final visual lock should still replace them with the exact Figma-exported icon assets if Dev Mode provides different paths, stroke widths, or fills.
