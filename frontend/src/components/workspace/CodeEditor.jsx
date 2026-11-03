import React from 'react';
import Editor from '@monaco-editor/react';

export default function CodeEditor({ value, onChange, language = 'java', readOnly = false, height = '450px' }) {
  return (
    <div className="w-full rounded-lg overflow-hidden border border-slate-700 shadow-inner bg-[#1e1e1e]">
      <div className="px-4 py-2 bg-slate-900 border-b border-slate-800 flex items-center justify-between text-xs text-slate-400">
        <span className="font-mono text-2xs text-slate-300">Solution.java (OpenJDK 14)</span>
        <span className="text-2xs text-slate-500 font-mono">UTF-8 • Tab: 4 spaces</span>
      </div>
      <Editor
        height={height}
        language={language}
        value={value}
        onChange={(val) => onChange && onChange(val || '')}
        theme="vs-dark"
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 13,
          fontFamily: "'Fira Code', 'JetBrains Mono', Consolas, monospace",
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          tabSize: 4,
          automaticLayout: true,
          padding: { top: 12, bottom: 12 },
        }}
      />
    </div>
  );
}

