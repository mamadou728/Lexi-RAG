import { DocumentData } from "@/lib/types";

interface DocumentViewerProps {
  document?: DocumentData | null;
}

export default function DocumentViewer({ document }: DocumentViewerProps) {
  if (!document) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <p className="text-gray-500 text-lg">No file opened yet</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto bg-gray-100 p-8">
      {/* The Paper Sheet */}
      <div className="max-w-3xl mx-auto bg-white min-h-[800px] shadow-sm border border-gray-200 p-12">
        
        {/* Header of the Document */}
        <div className="border-b-2 border-black pb-4 mb-8">
          <h1 className="text-3xl font-serif font-bold text-gray-900 mb-2">{document.title}</h1>
          <div className="text-sm text-gray-500 font-mono">DATE: {document.date}</div>
        </div>

        {/* The Body Content */}
        <div className="font-serif text-lg leading-relaxed text-gray-800 space-y-6">
          <p>
            {document.content}
            {/* Simulation of more text */}
             Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
             <span className="bg-yellow-200 px-1 mx-1 cursor-pointer" title="AI Reference #1">
               Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
             </span>
             Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
          </p>
          <p>
             Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
          </p>
        </div>
      </div>
    </div>
  );
}