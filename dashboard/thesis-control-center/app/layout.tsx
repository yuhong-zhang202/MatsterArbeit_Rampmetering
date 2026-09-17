import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "论文研究控制台",
  description: "用于管理论文结构、任务进度、参考文献、导师意见和仿真实验的本地控制台。",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className="antialiased">{children}</body>
    </html>
  );
}
