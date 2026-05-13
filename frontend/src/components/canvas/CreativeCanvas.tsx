"use client";

import { Canvas } from "@react-three/fiber";
import { Stars, Grid } from "@react-three/drei";
import { motion } from "framer-motion";
import { Suspense } from "react";
import { resolveStudioTheme, type StudioThemeId } from "@/lib/themePresets";

/**
 * Renders the theme-aware Three.js background elements behind the Studio shell.
 */
function Background({ themeId }: { themeId?: StudioThemeId }) {
    const theme = resolveStudioTheme(themeId);

    return (
        <>
            <color attach="background" args={[theme.background]} />
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
            <Grid
                infiniteGrid
                fadeDistance={50}
                sectionColor={theme.grid}
                cellColor={theme.accent}
                sectionSize={10}
                cellSize={1}
                sectionThickness={1}
                cellThickness={0.5}
            />
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} />
        </>
    );
}

/**
 * Full-screen animated background canvas used by the Studio home workspace.
 */
export default function CreativeCanvas({ themeId }: { themeId?: StudioThemeId }) {
    const theme = resolveStudioTheme(themeId);

    return (
        <div className="absolute inset-0 z-0 w-full h-full overflow-hidden bg-background">
            <Canvas camera={{ position: [0, 5, 10], fov: 60 }}>
                <Suspense fallback={null}>
                    <Background themeId={theme.id} />
                </Suspense>
            </Canvas>

            {/* Overlay gradient for UI readability */}
            <div className="absolute inset-0 pointer-events-none bg-gradient-to-b from-background/20 via-transparent to-background/50" />

            {/* Subtle animated wash keeps themes visible without adding decorative blobs. */}
            <motion.div
                className="absolute inset-0 pointer-events-none opacity-20 mix-blend-screen"
                animate={{
                    background: [
                        `linear-gradient(120deg, transparent 0%, ${theme.grid}22 46%, transparent 100%)`,
                        `linear-gradient(140deg, transparent 0%, ${theme.accent}1f 52%, transparent 100%)`,
                        `linear-gradient(120deg, transparent 0%, ${theme.grid}22 46%, transparent 100%)`
                    ]
                }}
                transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
            />
        </div>
    );
}
