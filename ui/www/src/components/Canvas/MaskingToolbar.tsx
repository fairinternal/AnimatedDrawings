import React from "react";
import classnames from "classnames";
import UndoIcon from "../../assets/customIcons/undo.svg";
import { Row, Col } from "react-bootstrap";
import useMaskingStore from "../../hooks/useMaskingStore";

const MaskingToolbar = () => {
  const {
    tool,
    penSize,
    lines,
    setTool,
    setPenSize,
    setLines,
  } = useMaskingStore();

  const handleReset = () => {
    if (!lines.length) {
      return;
    }
    setLines([]);
  };

  const handleUndo = () => {
    if (!lines.length) {
      return;
    }
    let newLines = lines.slice(0, -1);
    setLines(newLines);
  };

  return (
    <Row className="mx-0 tools-wrapper">
      <Col>
        <Row>
          <button
            className={classnames("sm-button-icon mr-2", {
              "bg-primary text-white": tool === "pen",
            })}
            onClick={() => setTool("pen")}
          >
            <i className="bi bi-pencil-fill" />
          </button>
          <button
            className={classnames("sm-button-icon mr-2", {
              "bg-primary text-white": tool === "eraser",
            })}
            onClick={() => setTool("eraser")}
          >
            <i className="bi bi-eraser-fill" />
          </button>
          <div className="pens-wrapper">
            <form className="pens">
              <label className="label0 d-none d-md-block">
                <input
                  type="radio"
                  name="radio"
                  value={3}
                  checked={penSize === 3}
                  onChange={() => setPenSize(3)}
                />
                <span></span>
              </label>
              <label className="label1">
                <input
                  type="radio"
                  name="radio"
                  value={5}
                  checked={penSize === 5}
                  onChange={() => setPenSize(5)}
                />
                <span></span>
              </label>
              <label className="label2">
                <input
                  type="radio"
                  name="radio"
                  value={15}
                  checked={penSize === 15}
                  onChange={() => setPenSize(15)}
                />
                <span></span>
              </label>
              <label className="label3">
                <input
                  type="radio"
                  name="radio"
                  value={26}
                  checked={penSize === 26}
                  onChange={() => setPenSize(26)}
                />
                <span></span>
              </label>
            </form>
          </div>
        </Row>
      </Col>
      <Col>
        <Row className="justify-content-end">
          <button
            className="sm-button-icon mr-2"
            onClick={handleUndo}
          >
            <img src={UndoIcon} alt="icon" />
          </button>

          <button
            className="md-button-reset p-0"
            onClick={handleReset}
          >
            Reset mask
          </button>
        </Row>
      </Col>
    </Row>
  );
};

export default MaskingToolbar;