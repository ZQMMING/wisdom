/**
 * 河图母题 — 静态 SVG 容器
 * 整体作为 .hero-transition__hetu 的内容，CSS 动画在父容器上跑
 */

import hetuSvg from '../../assets/hetu.svg?raw';

export function HetuEmblem() {
  return (
    <div
      className="hero-transition__hetu"
      aria-hidden="true"
      dangerouslySetInnerHTML={{ __html: hetuSvg }}
    />
  );
}
