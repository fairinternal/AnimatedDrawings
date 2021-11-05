import React from "react";
import image_1 from "../../assets/drawings_examples/step3/image_1.png";
import image_2 from "../../assets/drawings_examples/step3/image_2.png";

const Step3 = () => {
  return (
    <div className="step-actions-container bottom-shadow">
      <h1 className="step-title">
        Finding the <span className="text-info">Human-Like</span> Character
      </h1>
      <p>We’ve identified the character and put a box around it.</p>
      <p>Is the box too small for the character? If so, adjust the box.</p>
      <div className="drawing-example-wrapper">
        <img src={image_1} alt="Img1" />
      </div>
      <p>Is the box too big for the character? If so, adjust the box.</p>
      <div className="drawing-example-wrapper">
        <img src={image_2} alt="Img2" />
      </div>
      <p>If everything looks fine, hit 'Next'.</p>
    </div>
  );
};

export default Step3;
