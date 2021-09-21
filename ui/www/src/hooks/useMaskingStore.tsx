import create from "zustand";

interface Line {
  tool: string;
  penSize: number;
  points: Array<number>
}

type MaskingState = {
  tool: string;
  penSize: number;
  lines: Line[];
  blackLines: Line[];
  maskBase64: string;
  setTool:(tool: string) => void;
  setPenSize: (penSize: any) => void;
  setLines: (lines: Line[] ) => void;
  setBlackLines: (lines: Line[] ) => void;
  setMaskBase64 : (data: string | any) => void;
};

const useMaskingStore = create<MaskingState>((set) => ({
  tool: "eraser",
  penSize: 3,
  lines: [],
  blackLines: [],
  maskBase64: "",
  setTool: (tool) => set(() => ({ tool: tool })),
  setPenSize: (number) => set(() => ({ penSize: number })),
  setLines: (newLines) => set(() => ({lines : newLines})),
  setBlackLines: (newLines) => set(() => ({blackLines : newLines})),
  setMaskBase64: (data) => set(() => ({ maskBase64 : data}))
}));

export default useMaskingStore;
