import { useState, useEffect, useRef } from "react";
import IconButton from "@mui/material/IconButton";
import CloseIcon from "@mui/icons-material/Close";
import CheckIcon from "@mui/icons-material/Check";
import EditIcon from "@mui/icons-material/Edit";
import Tooltip from "@mui/material/Tooltip";
import Popover from "@mui/material/Popover";
import TextField from "@mui/material/TextField";
import { makeStyles } from "@mui/styles";

const useStyles = makeStyles({
  diffComponent: {
    position: "relative",
    display: "inline-block",
    cursor: "pointer",
  },
  icons: {
    display: "flex",
    gap: "4px",
    alignItems: "center",
  },
  popoverContent: {
    padding: "8px",
    maxWidth: "300px",
  },
  substitutionText: {
    display: "inline-flex",
    alignItems: "center",
  },
  arrow: {
    margin: "0 5px",
  },
  editingContainer: {
    display: "flex",
    alignItems: "center",
    gap: "8px", // Расстояние между текстовым полем и кнопками
  },
  textField: {
    flexGrow: 1,
  },
});

const DiffComponent = ({ type, text, originalText, newText }) => {
  const classes = useStyles();
  const [status, setStatus] = useState("pending"); // 'pending', 'accepted', 'rejected', 'editing'
  const [editedNewText, setEditedNewText] = useState(newText || text || "");
  const [anchorEl, setAnchorEl] = useState(null);
  const componentRef = useRef(null);

  const handleClick = (e) => {
    e.stopPropagation();
    if (status !== "editing") {
      setAnchorEl(e.currentTarget);
    }
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleAccept = () => {
    setStatus("accepted");
    setAnchorEl(null); // Закрываем попап
  };

  const handleReject = () => {
    setStatus("rejected");
    setAnchorEl(null); // Закрываем попап
  };

  const handleEdit = () => {
    setStatus("editing");
    setAnchorEl(null); // Закрываем попап
  };

  const saveEdit = () => {
    setStatus("accepted");
  };

  const cancelEdit = () => {
    setStatus("pending");
    setEditedNewText(newText || text || ""); // Сбрасываем изменения
  };

  // Закрываем попап, если статус изменился
  useEffect(() => {
    if (status !== "pending") {
      setAnchorEl(null);
    }
  }, [status]);

  const open = Boolean(anchorEl);
  const id = open ? "diff-popover" : undefined;

  let displayContent = null;
  let className = "";

  if (status === "rejected") {
    // Показываем оригинальный текст
    displayContent = <span>{originalText}</span>;
    className = "";
  } else if (status === "accepted") {
    displayContent = <span>{editedNewText}</span>;
    className = type === "substitution" ? "" : type;
  } else if (status === "editing") {
    displayContent = (
      <div className={classes.editingContainer}>
        <TextField
          className={classes.textField}
          value={editedNewText}
          onChange={(e) => setEditedNewText(e.target.value)}
          size="small"
          autoFocus
        />
        <div className={classes.icons}>
          <Tooltip title="Cancel">
            <IconButton onClick={cancelEdit} size="small">
              <CloseIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          <Tooltip title="Save">
            <IconButton onClick={saveEdit} size="small">
              <CheckIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </div>
      </div>
    );
    className = type;
  } else {
    // Ожидание действий
    if (type === "substitution") {
      displayContent = (
        <span className={classes.substitutionText}>
          <span className="removed">{originalText}</span>
          <span className={classes.arrow}>→</span>
          <span className="added">{newText}</span>
        </span>
      );
    } else if (type === "added") {
      displayContent = <span className="added">{newText}</span>;
    } else if (type === "removed") {
      displayContent = <span className="removed">{originalText}</span>;
    } else {
      displayContent = <span>{newText}</span>;
    }
    className = type;
  }

  return (
    <span
      ref={componentRef}
      className={`${classes.diffComponent} ${className}`}
      onClick={handleClick}
    >
      {displayContent}
      {status !== "editing" && (
        <Popover
          id={id}
          open={open}
          anchorEl={anchorEl}
          onClose={handleClose}
          disableRestoreFocus
          anchorOrigin={{
            vertical: "top",
            horizontal: "left",
          }}
          transformOrigin={{
            vertical: "bottom",
            horizontal: "center",
          }}
        >
          <div className={classes.popoverContent}>
            <div className={classes.icons}>
              <Tooltip title="Reject">
                <IconButton onClick={handleReject} size="small">
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Accept">
                <IconButton onClick={handleAccept} size="small">
                  <CheckIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="Edit">
                <IconButton onClick={handleEdit} size="small">
                  <EditIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </div>
          </div>
        </Popover>
      )}
    </span>
  );
};

export default DiffComponent;
