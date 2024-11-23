import { useUser } from "@clerk/clerk-react";
import Header from "../components/Header";
function DragAndDropPage() {
  const { isSignedIn } = useUser();

  return (
    <div className="container text-center py-5">
      {isSignedIn ? (
        <>
          <Header />
          <h1 className="mb-4">Drag and Drop Page</h1>
          <div
            className="border p-5 my-3"
            style={{
              borderRadius: "10px",
              borderStyle: "dashed",
              borderColor: "#ccc",
            }}
          >
            <p className="text-muted">
              Drag and drop a PDF document here or click to upload.
            </p>
          </div>
        </>
      ) : (
        <h1>You are not authorized to access this page</h1>
      )}
    </div>
  );
}

export default DragAndDropPage;
