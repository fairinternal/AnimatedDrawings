import React, { useRef, useEffect, useState } from "react";
import { Spinner } from "react-bootstrap";
import useDrawingStore from "../../hooks/useDrawingStore";
import useStepperStore from "../../hooks/useStepperStore";
import { useDrawingApi } from "../../hooks/useDrawingApi";
import BoundingBoxStage from "./BoundingBoxStage";

export interface BoundingBox {
  x: number;
  width: number;
  y: number;
  height: number;
  id: string;
}

const calculateRatio = (
  canvasWidth: number,
  canvasHeight: number,
  oW: number,  //Original image width
  oH: number,  //Original image height
) => {
  if (oH >= oW && canvasHeight >= canvasWidth) {
    return canvasHeight / oH < 1 ? canvasHeight / oH : 1;
  } else if (oH < oW && canvasHeight >= canvasWidth) {
    return canvasHeight / oW < 1 ? canvasHeight / oW : 1
  } else if (oH >= oW && canvasHeight < canvasWidth) {
    return canvasWidth / oH < 1 ? canvasWidth / oH : 1;
  } else {
    return canvasWidth / oW < 1 ? canvasWidth / oW : 1;
  }
};

const CanvasBoundingBox = () => {
  const canvasWindow = useRef<HTMLDivElement | any>(null);
  const { currentStep, setCurrentStep } = useStepperStore();
  const {
    uuid,
    imageUrlPose,
    originalDimension,
    boundingBox,
    setBox,
    setCroppedImgDimensions
  } = useDrawingStore();
  const {
    isLoading,
    getBoundingBox,
    setBoundingBox,
  } = useDrawingApi((err) => {});

  const [iWidth, setImageWidth] = useState(0);
  const [iHeight, setImageHeight] = useState(0);
  const [imgRatio, setImgRatio] = useState(0);

  /**
   * When the components mounts, invokes API to fetch json bounding box coordinates.
   * The component will only rerender when the uuid dependency changes.
   * exhaustive-deps eslint warning was diable as no more dependencies are really necesary as side effects.
   * Contrary to this, including other function dependencies will trigger infinite loop rendereing.
   */
  useEffect(() => {
    const fetchBB = async () => {
      try {
        const tempImage = new Image();
        if (imageUrlPose !== null && imageUrlPose !== undefined)
          tempImage.src = imageUrlPose; // cropped image base64

        tempImage.onload = (e) => {
          if (canvasWindow.current) {
            setCroppedImgDimensions({
              width: tempImage.naturalWidth,
              height: tempImage.naturalHeight,
            });
          }
        };

        const ratio = calculateRatio(
          canvasWindow.current?.offsetWidth -20,
          canvasWindow.current?.offsetHeight -20,
          originalDimension.width,
          originalDimension.height
        );
        
        const calculatedWidth = originalDimension.width * ratio;
        const calculatedHeight = originalDimension.height * ratio;
        setImageWidth(calculatedWidth);
        setImageHeight(calculatedHeight);
        setImgRatio(ratio);

        await getBoundingBox(uuid!, (data) => {
          setBox({
            x:
              data.x1 * ratio +
              (canvasWindow.current?.offsetWidth / 2 - calculatedWidth / 2),
            width: data.x2 * ratio - data.x1 * ratio,
            y:
              data.y1 * ratio +
              (canvasWindow.current?.offsetHeight / 2 - calculatedHeight / 2),
            height: data.y2 * ratio - data.y1 * ratio,
            id: "1",
          });
        });
      } catch (error) {
        console.log(error);
      }
    };

    if (uuid !== "") fetchBB();

    return () => {};
  }, [uuid, canvasWindow.current]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleClick = async (clickType: string) => {
    try {
      if (null === uuid && undefined === uuid) {
        return;
      }
      //Send new bounding box attributes.
      if (clickType === "next") {
        let xOffset = canvasWindow.current?.offsetWidth / 2 - iWidth / 2;
        let yOffset = canvasWindow.current?.offsetHeight / 2 - iHeight / 2;
        const coordinates = {
          x1: Math.round(
            (boundingBox.x - xOffset) / imgRatio >= 0
              ? (boundingBox.x - xOffset) / imgRatio
              : 0
          ),
          x2: Math.round(
            boundingBox.width / imgRatio +
              boundingBox.x / imgRatio -
              xOffset / imgRatio
          ),
          y1: Math.round(
            (boundingBox.y - yOffset) / imgRatio >= 0
              ? (boundingBox.y - yOffset) / imgRatio
              : 0
          ),
          y2: Math.round(
            boundingBox.height / imgRatio +
              boundingBox.y / imgRatio -
              yOffset / imgRatio
          ),
        };
       
        await setBoundingBox(uuid!, coordinates, () => {
          console.log("Bounding box loaded.");
        });
        setCurrentStep(currentStep + 1);
      }
    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div className="canvas-wrapper">
      <div ref={canvasWindow} className="canvas-background border border-dark">
        <BoundingBoxStage
          canvasWidth={canvasWindow.current?.offsetWidth}
          canvasHeight={canvasWindow.current?.offsetHeight}
          imageWidth={iWidth}
          imageHeight={iHeight}
        />
      </div>

      <div className="mt-3">
        <button
          className="buttons large-button"
          disabled={isLoading}
          onClick={() => handleClick("next")}
        >
          {isLoading ? (
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
            />
          ) : (
            <>
              Next <i className="bi bi-arrow-right ml-1" />{" "}
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default CanvasBoundingBox;