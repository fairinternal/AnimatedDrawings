import React, { useState, Fragment } from "react";
import classnames from "classnames";
import { Row, Button } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import AnimationTypes from "../../utils/AnimationTypes";

const Step7 = () => {
  const { animationType, setAnimationType } = useDrawingStore();
  const [group, setGroup] = useState("all");

  const groups = AnimationTypes.reduce((r, a) => {
    r[a.group] = r[a.group] || [];
    r[a.group].push(a);
    return r;
  }, Object.create(null));

  const allGroup = AnimationTypes.map((i: any, index: number) => {
    return (
      <Fragment key={index}>
        <div
          className={classnames("sm-grid-item", {
            "item-grid-selected": i.name === animationType,
          })}
          onClick={() => setAnimationType(i.name)}
        >
          <img src={i.gif} alt="" />
        </div>
      </Fragment>
    );
  });

  const danceGroup = groups["dance"].map((i: any, index: number) => {
    return (
      <Fragment key={index}>
        <div
          className={classnames("sm-grid-item", {
            "item-grid-selected": i.name === animationType,
          })}
          onClick={() => setAnimationType(i.name)}
        >
          <img src={i.gif} alt="" />
        </div>
      </Fragment>
    );
  });

  const funnyGroup = groups["funny"].map((i: any, index: number) => {
    return (
      <Fragment key={index}>
        <div
          className={classnames("sm-grid-item", {
            "item-grid-selected": i.name === animationType,
          })}
          onClick={() => setAnimationType(i.name)}
        >
          <img src={i.gif} alt="" />
        </div>
      </Fragment>
    );
  });

  const jumpsGroup = groups["jumps"].map((i: any, index: number) => {
    return (
      <Fragment key={index}>
        <div
          className={classnames("sm-grid-item", {
            "item-grid-selected": i.name === animationType,
          })}
          onClick={() => setAnimationType(i.name)}
        >
          <img src={i.gif} alt="" />
        </div>
      </Fragment>
    );
  });

  const walkingGroup = groups["walks"].map((i: any, index: number) => {
    return (
      <Fragment key={index}>
        <div
          className={classnames("sm-grid-item", {
            "item-grid-selected": i.name === animationType,
          })}
          onClick={() => setAnimationType(i.name)}
        >
          <img src={i.gif} alt="" />
        </div>
      </Fragment>
    );
  });

  const renderGroup = () => {
    switch (group) {
      case "all":
        return <div className="grid-container">{allGroup}</div>;
      case "dance":
        return <div className="grid-container">{danceGroup}</div>;
      case "funny":
        return <div className="grid-container">{funnyGroup}</div>;
      case "jumps":
        return <div className="grid-container">{jumpsGroup}</div>;
      case "walks":
        return <div className="grid-container">{walkingGroup}</div>;
      default:
        return <Fragment></Fragment>;
    }
  };

  return (
      <div className="step-actions-container-animation">
        <h1 className="step-title ml-2">
          Add <span className="text-info">Animation</span>
        </h1>
        <p className="ml-2">Choose one of the motions below to see your character perform it!</p>

        <Row className="px-0 m-0 ml-lg-2 nav-pills">
          <Button
            variant={group === "all" ? "primary" : "outline-primary"}
            size="sm"
            onClick={() => setGroup("all")}
          >
            ALL
          </Button>
          <Button
            variant={group === "dance" ? "primary" : "outline-primary"}
            size="sm"
            onClick={() => setGroup("dance")}
          >
            DANCE
          </Button>
          <Button
            variant={group === "funny" ? "primary" : "outline-primary"}
            size="sm"
            onClick={() => setGroup("funny")}
          >
            FUNNY
          </Button>
          <Button
            variant={group === "jumps" ? "primary" : "outline-primary"}
            size="sm"
            onClick={() => setGroup("jumps")}
          >
            JUMPING
          </Button>
          <Button
            variant={group === "walks" ? "primary" : "outline-primary"}
            size="sm"
            onClick={() => setGroup("walks")}
          >
            WALKING
          </Button>
        </Row>

        <Row className="px-0 m-0 mt-4">{renderGroup()}</Row>
      </div>
  );
};

export default Step7;
