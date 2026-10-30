"use client";

import { useEffect, useRef } from "react";
import { cn } from "../lib/cn";
import { starfield as cfg } from "../tokens";

interface Star {
  x: number;
  y: number;
  r: number;
  phase: number;
  base: number;
}

interface Shooter {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  len: number;
}

/**
 * Low-cost animated starfield with subtle shooting stars.
 *
 * Accessibility: when the user prefers reduced motion, a single static frame is
 * painted and no animation loop runs. The canvas is purely decorative
 * (aria-hidden) and sits behind content.
 */
export function Starfield({ className }: { className?: string }) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const reduceMotion =
      typeof window !== "undefined" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    let stars: Star[] = [];
    let shooters: Shooter[] = [];
    let raf = 0;
    let lastShot = 0;
    let dpr = Math.min(window.devicePixelRatio || 1, 2);

    function seed() {
      const w = canvas!.clientWidth;
      const h = canvas!.clientHeight;
      const count = Math.min(
        cfg.maxStars,
        Math.round(((w * h) / 100_000) * cfg.densityPer100kPx),
      );
      stars = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 1.3 + 0.3,
        phase: Math.random() * Math.PI * 2,
        base: Math.random() * 0.4 + 0.4,
      }));
    }

    function resize() {
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = canvas!.clientWidth;
      const h = canvas!.clientHeight;
      canvas!.width = Math.max(1, Math.floor(w * dpr));
      canvas!.height = Math.max(1, Math.floor(h * dpr));
      ctx!.setTransform(dpr, 0, 0, dpr, 0, 0);
      seed();
      if (reduceMotion) paint(0);
    }

    function spawnShooter() {
      const w = canvas!.clientWidth;
      const speed = 5 + Math.random() * 3;
      shooters.push({
        x: Math.random() * w * 0.7,
        y: Math.random() * 120,
        vx: speed,
        vy: speed * 0.35,
        life: 1,
        len: 90 + Math.random() * 70,
      });
    }

    function paint(t: number) {
      const w = canvas!.clientWidth;
      const h = canvas!.clientHeight;
      ctx!.clearRect(0, 0, w, h);

      for (const s of stars) {
        const tw = reduceMotion
          ? s.base
          : s.base + Math.sin(t * cfg.twinkleSpeed + s.phase) * 0.35;
        const alpha = Math.max(0.1, Math.min(1, tw));
        ctx!.beginPath();
        ctx!.fillStyle = `rgba(150, 215, 255, ${alpha})`;
        ctx!.arc(s.x, s.y, s.r, 0, Math.PI * 2);
        ctx!.fill();
      }

      if (!reduceMotion) {
        shooters = shooters.filter((sh) => sh.life > 0);
        for (const sh of shooters) {
          const tailX = sh.x - (sh.vx / Math.hypot(sh.vx, sh.vy)) * sh.len;
          const tailY = sh.y - (sh.vy / Math.hypot(sh.vx, sh.vy)) * sh.len;
          const grad = ctx!.createLinearGradient(sh.x, sh.y, tailX, tailY);
          grad.addColorStop(0, `rgba(54, 230, 255, ${0.85 * sh.life})`);
          grad.addColorStop(1, "rgba(54, 230, 255, 0)");
          ctx!.strokeStyle = grad;
          ctx!.lineWidth = 2;
          ctx!.beginPath();
          ctx!.moveTo(sh.x, sh.y);
          ctx!.lineTo(tailX, tailY);
          ctx!.stroke();
          sh.x += sh.vx;
          sh.y += sh.vy;
          sh.life -= 0.012;
        }
      }
    }

    function loop(t: number) {
      paint(t);
      if (
        t - lastShot > cfg.shootingStarIntervalMs &&
        shooters.length < cfg.shootingStarCount
      ) {
        spawnShooter();
        lastShot = t;
      }
      raf = requestAnimationFrame(loop);
    }

    resize();
    window.addEventListener("resize", resize);
    if (!reduceMotion) raf = requestAnimationFrame(loop);

    return () => {
      window.removeEventListener("resize", resize);
      if (raf) cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      className={cn("pointer-events-none absolute inset-0 h-full w-full", className)}
    />
  );
}
