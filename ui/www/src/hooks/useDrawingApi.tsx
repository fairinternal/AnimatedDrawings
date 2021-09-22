import axios, { AxiosRequestConfig } from "axios";
import { useState } from "react";
import {} from "../EnvConfig";

const apiHost = window._env_.REACT_APP_API_HOST;

export function useDrawingApi(onError: (error: Error) => void) {
  const [isLoading, setIsLoading] = useState(false);

  enum ApiPath {
    UploadImage = "upload_image",

    SetConsentAnswer = "set_consent_answer",
    GetBoundingBox = "get_bounding_box_coordinates",
    SetBoundingBox = "set_bounding_box_coordinates",
    GetJointLocations = "get_joint_locations_json",
    SetJointLocations = "set_joint_locations_json",
    GetCroppedImage = "get_cropped_image",
    GetAnimation = "get_animation",
    GetMask = "get_mask",
    SetMask = "set_mask",
  }

  const DEFAULT_CONFIG = {
    timeout: 60000,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  };

  async function invokePost(
    path: string,
    data: any,
    onResult: (result: any) => void,
    config: AxiosRequestConfig = DEFAULT_CONFIG
  ) {
    try {
      setIsLoading(true);

      const result = await axios.post(`${apiHost}/${path}`, data, config);
      onResult(result.data);
    } catch (error) {
      console.log(error);
      onError(error as Error);
    } finally {
      setIsLoading(false);
    }
  }

  // Upload an image file to the ML model
  const uploadImage = async function (
    file: File,
    onResult: (result: any) => void
  ) {
    const form = new FormData();
    if (file !== null) {
      form.append("file", file);
    }
    await invokePost(ApiPath.UploadImage, form, onResult);
  };

  // Set Consent Answer
  const setConsentAnswer = async function (
    uuid: string,
    data: any,
    onResult: (result: any) => void
  ) {
    const form = new FormData();
    if (uuid) {
      form.set("uuid", uuid);
    }

    form.set("consent_response", data);
    await invokePost(ApiPath.SetConsentAnswer, form, onResult);
  };

  // Get Bounding Box
  const getBoundingBox = async function (
    uuid: string,
    onResult: (result: any) => void
  ) {

    const form = new FormData();
    if (uuid) {
      form.set("uuid", uuid);
    }
    await invokePost(ApiPath.GetBoundingBox, form, onResult);
  };

  // Set Bounding Box
  const setBoundingBox = async function (
    uuid: string,
    data: any,
    onResult: (result: any) => void
  ) {
    const form = new FormData();
    if (uuid) {
      form.set("uuid", uuid);
    }

    form.set("bounding_box_coordinates", JSON.stringify(data));
    await invokePost(ApiPath.SetBoundingBox, form, onResult);
  };

  // Get Joint Locations
  const getJointLocations = async function (
    uuid: string,
    onResult: (result: any) => void
  ) {
    // try {

    const form = new FormData();
    if (uuid) {
      form.set("uuid", uuid);
    }
    await invokePost(ApiPath.GetJointLocations, form, onResult);
  };

  // Set JointLocations
  const setJointLocations = async function (
    uuid: string,
    data: any,
    onResult: (result: any) => void
  ) {
    // try {

    const form = new FormData();
    if (uuid) {
      form.set("uuid", uuid);
    }

    form.set("joint_location_json", JSON.stringify(data));
    await invokePost(ApiPath.SetJointLocations, form, onResult);
  };

  // Get Mask
  const getMask = async function (
    uuid: string,
    onResult: (result: any) => void
  ) {
    const form = new FormData();
    if (uuid) {
      form.set("uuid", uuid);
    }
    await invokePost(ApiPath.GetMask, form, onResult, {
      ...DEFAULT_CONFIG,
      responseType: "blob",
    });
  };

  // Set Mask
  const setMask = async function (
    uuid: string,
    file: File,
    onResult: (result: any) => void
  ) {
    const form = new FormData();
    if (uuid) {
      form.set("uuid", uuid);
    }
    if (file !== null) {
      form.set("file", file);
    }
    await invokePost(ApiPath.SetMask, form, onResult, {
      ...DEFAULT_CONFIG,
      responseType: "blob",
    });
  };

  // Get Cropped Image
  const getCroppedImage = async function (
    uuid: string,
    onResult: (result: any) => void
  ) {
    // try {

    const form = new FormData();
    if (uuid) {
      form.set("uuid", uuid);
    }
    await invokePost(ApiPath.GetCroppedImage, form, onResult, {
      ...DEFAULT_CONFIG,
      responseType: "blob",
    });
  };

  // Get Final Animation Video
  const getAnimation = async function (
    uuid: string,
    animation: string = "wave_hello_3",
    onResult: (result: any) => void
  ) {
    // try {

    const form = new FormData();
    form.set("animation", animation);
    if (uuid) {
      form.set("uuid", uuid);
    }
    await invokePost(ApiPath.GetAnimation, form, onResult, {
      ...DEFAULT_CONFIG,
      responseType: "arraybuffer",
    });
  };

  return {
    isLoading,
    uploadImage,
    setConsentAnswer,
    getBoundingBox,
    setBoundingBox,
    getJointLocations,
    setJointLocations,
    getCroppedImage,
    getAnimation,
    getMask,
    setMask,
  };
}
