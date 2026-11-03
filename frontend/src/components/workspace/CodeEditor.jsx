import React from 'react';
import Editor from '@monaco-editor/react';

export default function CodeEditor({
  value,
  onChange,
  language = 'java',
  readOnly = false,
  height = '480px',
}) {
  return (
    <div className="w-full rounded-xl overflow-hidden border border-slate-700 shadow-xl bg-[#1e1e1e] flex flex-col">
      {/* Editor Header */}
      <div className="px-4 py-2.5 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400 select-none">
        <div className="flex items-center space-x-2">
          <div className="flex space-x-1.5">
            <div className="w-3 h-3 rounded-full bg-rose-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-amber-500/80"></div>
            <div className="w-3 h-3 rounded-full bg-emerald-500/80"></div>
          </div>
          <span className="font-mono text-xs font-semibold text-slate-200 ml-2">Main.java</span>
          <span className="px-2 py-0.5 rounded text-2xs bg-slate-800 text-slate-400 font-mono">
            OpenJDK 17
          </span>
        </div>
        <div className="flex items-center space-x-4 text-2xs text-slate-400 font-mono">
          <span>Language: Java</span>
          <span>Spaces: 4</span>
          <span>UTF-8</span>
        </div>
      </div>

      {/* Monaco Editor Container */}
      <div className="flex-1 min-h-[400px]">
        <Editor
          height={height}
          language={language}
          value={value}
          onChange={(val) => onChange && onChange(val || '')}
          theme="vs-dark"
          loading={
            <div className="flex items-center justify-center h-full bg-[#1e1e1e] text-slate-400 text-xs font-mono">
              Loading Monaco Java Editor...
            </div>
          }
          options={{
            readOnly,
            minimap: { enabled: false },
            fontSize: 13.5,
            fontFamily: "'JetBrains Mono', 'Fira Code', Menlo, Monaco, Consolas, monospace",
            lineNumbers: 'on',
            lineNumbersMinChars: 3,
            glyphMargin: false,
            folding: true,
            scrollBeyondLastLine: false,
            tabSize: 4,
            insertSpaces: true,
            automaticLayout: true,
            bracketPairColorization: { enabled: true },
            formatOnType: true,
            formatOnPaste: true,
            cursorBlinking: 'smooth',
            cursorSmoothCaretAnimation: 'on',
            padding: { top: 12, bottom: 12 },
            suggestOnTriggerCharacters: true,
            renderLineHighlight: 'all',
          }}
        />
      </div>
    </div>
  );
}
