"use strict";
/*
 * ATTENTION: An "eval-source-map" devtool has been used.
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file with attached SourceMaps in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(() => {
var exports = {};
exports.id = "app/api/auth/[...nextauth]/route";
exports.ids = ["app/api/auth/[...nextauth]/route"];
exports.modules = {

/***/ "../../client/components/action-async-storage.external":
/*!*******************************************************************************!*\
  !*** external "next/dist/client/components/action-async-storage.external.js" ***!
  \*******************************************************************************/
/***/ ((module) => {

module.exports = require("next/dist/client/components/action-async-storage.external.js");

/***/ }),

/***/ "../../client/components/request-async-storage.external":
/*!********************************************************************************!*\
  !*** external "next/dist/client/components/request-async-storage.external.js" ***!
  \********************************************************************************/
/***/ ((module) => {

module.exports = require("next/dist/client/components/request-async-storage.external.js");

/***/ }),

/***/ "../../client/components/static-generation-async-storage.external":
/*!******************************************************************************************!*\
  !*** external "next/dist/client/components/static-generation-async-storage.external.js" ***!
  \******************************************************************************************/
/***/ ((module) => {

module.exports = require("next/dist/client/components/static-generation-async-storage.external.js");

/***/ }),

/***/ "next/dist/compiled/next-server/app-page.runtime.dev.js":
/*!*************************************************************************!*\
  !*** external "next/dist/compiled/next-server/app-page.runtime.dev.js" ***!
  \*************************************************************************/
/***/ ((module) => {

module.exports = require("next/dist/compiled/next-server/app-page.runtime.dev.js");

/***/ }),

/***/ "next/dist/compiled/next-server/app-route.runtime.dev.js":
/*!**************************************************************************!*\
  !*** external "next/dist/compiled/next-server/app-route.runtime.dev.js" ***!
  \**************************************************************************/
/***/ ((module) => {

module.exports = require("next/dist/compiled/next-server/app-route.runtime.dev.js");

/***/ }),

/***/ "assert":
/*!*************************!*\
  !*** external "assert" ***!
  \*************************/
/***/ ((module) => {

module.exports = require("assert");

/***/ }),

/***/ "buffer":
/*!*************************!*\
  !*** external "buffer" ***!
  \*************************/
/***/ ((module) => {

module.exports = require("buffer");

/***/ }),

/***/ "crypto":
/*!*************************!*\
  !*** external "crypto" ***!
  \*************************/
/***/ ((module) => {

module.exports = require("crypto");

/***/ }),

/***/ "events":
/*!*************************!*\
  !*** external "events" ***!
  \*************************/
/***/ ((module) => {

module.exports = require("events");

/***/ }),

/***/ "http":
/*!***********************!*\
  !*** external "http" ***!
  \***********************/
/***/ ((module) => {

module.exports = require("http");

/***/ }),

/***/ "https":
/*!************************!*\
  !*** external "https" ***!
  \************************/
/***/ ((module) => {

module.exports = require("https");

/***/ }),

/***/ "querystring":
/*!******************************!*\
  !*** external "querystring" ***!
  \******************************/
/***/ ((module) => {

module.exports = require("querystring");

/***/ }),

/***/ "url":
/*!**********************!*\
  !*** external "url" ***!
  \**********************/
/***/ ((module) => {

module.exports = require("url");

/***/ }),

/***/ "util":
/*!***********************!*\
  !*** external "util" ***!
  \***********************/
/***/ ((module) => {

module.exports = require("util");

/***/ }),

/***/ "zlib":
/*!***********************!*\
  !*** external "zlib" ***!
  \***********************/
/***/ ((module) => {

module.exports = require("zlib");

/***/ }),

/***/ "(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader.js?name=app%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute&page=%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute.ts&appDir=C%3A%5CUsers%5Chsana%5CwaqediA%C4%B0%5Cfrontend%5Cweb-console%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=C%3A%5CUsers%5Chsana%5CwaqediA%C4%B0%5Cfrontend%5Cweb-console&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!":
/*!****************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************!*\
  !*** ./node_modules/next/dist/build/webpack/loaders/next-app-loader.js?name=app%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute&page=%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute.ts&appDir=C%3A%5CUsers%5Chsana%5CwaqediA%C4%B0%5Cfrontend%5Cweb-console%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=C%3A%5CUsers%5Chsana%5CwaqediA%C4%B0%5Cfrontend%5Cweb-console&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D! ***!
  \****************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   originalPathname: () => (/* binding */ originalPathname),\n/* harmony export */   patchFetch: () => (/* binding */ patchFetch),\n/* harmony export */   requestAsyncStorage: () => (/* binding */ requestAsyncStorage),\n/* harmony export */   routeModule: () => (/* binding */ routeModule),\n/* harmony export */   serverHooks: () => (/* binding */ serverHooks),\n/* harmony export */   staticGenerationAsyncStorage: () => (/* binding */ staticGenerationAsyncStorage)\n/* harmony export */ });\n/* harmony import */ var next_dist_server_future_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next/dist/server/future/route-modules/app-route/module.compiled */ \"(rsc)/./node_modules/next/dist/server/future/route-modules/app-route/module.compiled.js\");\n/* harmony import */ var next_dist_server_future_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_future_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var next_dist_server_future_route_kind__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! next/dist/server/future/route-kind */ \"(rsc)/./node_modules/next/dist/server/future/route-kind.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! next/dist/server/lib/patch-fetch */ \"(rsc)/./node_modules/next/dist/server/lib/patch-fetch.js\");\n/* harmony import */ var next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__);\n/* harmony import */ var C_Users_hsana_waqediA_frontend_web_console_app_api_auth_nextauth_route_ts__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./app/api/auth/[...nextauth]/route.ts */ \"(rsc)/./app/api/auth/[...nextauth]/route.ts\");\n\n\n\n\n// We inject the nextConfigOutput here so that we can use them in the route\n// module.\nconst nextConfigOutput = \"standalone\"\nconst routeModule = new next_dist_server_future_route_modules_app_route_module_compiled__WEBPACK_IMPORTED_MODULE_0__.AppRouteRouteModule({\n    definition: {\n        kind: next_dist_server_future_route_kind__WEBPACK_IMPORTED_MODULE_1__.RouteKind.APP_ROUTE,\n        page: \"/api/auth/[...nextauth]/route\",\n        pathname: \"/api/auth/[...nextauth]\",\n        filename: \"route\",\n        bundlePath: \"app/api/auth/[...nextauth]/route\"\n    },\n    resolvedPagePath: \"C:\\\\Users\\\\hsana\\\\waqediAİ\\\\frontend\\\\web-console\\\\app\\\\api\\\\auth\\\\[...nextauth]\\\\route.ts\",\n    nextConfigOutput,\n    userland: C_Users_hsana_waqediA_frontend_web_console_app_api_auth_nextauth_route_ts__WEBPACK_IMPORTED_MODULE_3__\n});\n// Pull out the exports that we need to expose from the module. This should\n// be eliminated when we've moved the other routes to the new format. These\n// are used to hook into the route.\nconst { requestAsyncStorage, staticGenerationAsyncStorage, serverHooks } = routeModule;\nconst originalPathname = \"/api/auth/[...nextauth]/route\";\nfunction patchFetch() {\n    return (0,next_dist_server_lib_patch_fetch__WEBPACK_IMPORTED_MODULE_2__.patchFetch)({\n        serverHooks,\n        staticGenerationAsyncStorage\n    });\n}\n\n\n//# sourceMappingURL=app-route.js.map//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9ub2RlX21vZHVsZXMvbmV4dC9kaXN0L2J1aWxkL3dlYnBhY2svbG9hZGVycy9uZXh0LWFwcC1sb2FkZXIuanM/bmFtZT1hcHAlMkZhcGklMkZhdXRoJTJGJTVCLi4ubmV4dGF1dGglNUQlMkZyb3V0ZSZwYWdlPSUyRmFwaSUyRmF1dGglMkYlNUIuLi5uZXh0YXV0aCU1RCUyRnJvdXRlJmFwcFBhdGhzPSZwYWdlUGF0aD1wcml2YXRlLW5leHQtYXBwLWRpciUyRmFwaSUyRmF1dGglMkYlNUIuLi5uZXh0YXV0aCU1RCUyRnJvdXRlLnRzJmFwcERpcj1DJTNBJTVDVXNlcnMlNUNoc2FuYSU1Q3dhcWVkaUElQzQlQjAlNUNmcm9udGVuZCU1Q3dlYi1jb25zb2xlJTVDYXBwJnBhZ2VFeHRlbnNpb25zPXRzeCZwYWdlRXh0ZW5zaW9ucz10cyZwYWdlRXh0ZW5zaW9ucz1qc3gmcGFnZUV4dGVuc2lvbnM9anMmcm9vdERpcj1DJTNBJTVDVXNlcnMlNUNoc2FuYSU1Q3dhcWVkaUElQzQlQjAlNUNmcm9udGVuZCU1Q3dlYi1jb25zb2xlJmlzRGV2PXRydWUmdHNjb25maWdQYXRoPXRzY29uZmlnLmpzb24mYmFzZVBhdGg9JmFzc2V0UHJlZml4PSZuZXh0Q29uZmlnT3V0cHV0PXN0YW5kYWxvbmUmcHJlZmVycmVkUmVnaW9uPSZtaWRkbGV3YXJlQ29uZmlnPWUzMCUzRCEiLCJtYXBwaW5ncyI6Ijs7Ozs7Ozs7Ozs7Ozs7O0FBQXNHO0FBQ3ZDO0FBQ2M7QUFDMEM7QUFDdkg7QUFDQTtBQUNBO0FBQ0Esd0JBQXdCLGdIQUFtQjtBQUMzQztBQUNBLGNBQWMseUVBQVM7QUFDdkI7QUFDQTtBQUNBO0FBQ0E7QUFDQSxLQUFLO0FBQ0w7QUFDQTtBQUNBLFlBQVk7QUFDWixDQUFDO0FBQ0Q7QUFDQTtBQUNBO0FBQ0EsUUFBUSxpRUFBaUU7QUFDekU7QUFDQTtBQUNBLFdBQVcsNEVBQVc7QUFDdEI7QUFDQTtBQUNBLEtBQUs7QUFDTDtBQUN1SDs7QUFFdkgiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly93YXFlZGktd2ViLWNvbnNvbGUvPzliYjQiXSwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgQXBwUm91dGVSb3V0ZU1vZHVsZSB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL2Z1dHVyZS9yb3V0ZS1tb2R1bGVzL2FwcC1yb3V0ZS9tb2R1bGUuY29tcGlsZWRcIjtcbmltcG9ydCB7IFJvdXRlS2luZCB9IGZyb20gXCJuZXh0L2Rpc3Qvc2VydmVyL2Z1dHVyZS9yb3V0ZS1raW5kXCI7XG5pbXBvcnQgeyBwYXRjaEZldGNoIGFzIF9wYXRjaEZldGNoIH0gZnJvbSBcIm5leHQvZGlzdC9zZXJ2ZXIvbGliL3BhdGNoLWZldGNoXCI7XG5pbXBvcnQgKiBhcyB1c2VybGFuZCBmcm9tIFwiQzpcXFxcVXNlcnNcXFxcaHNhbmFcXFxcd2FxZWRpQcSwXFxcXGZyb250ZW5kXFxcXHdlYi1jb25zb2xlXFxcXGFwcFxcXFxhcGlcXFxcYXV0aFxcXFxbLi4ubmV4dGF1dGhdXFxcXHJvdXRlLnRzXCI7XG4vLyBXZSBpbmplY3QgdGhlIG5leHRDb25maWdPdXRwdXQgaGVyZSBzbyB0aGF0IHdlIGNhbiB1c2UgdGhlbSBpbiB0aGUgcm91dGVcbi8vIG1vZHVsZS5cbmNvbnN0IG5leHRDb25maWdPdXRwdXQgPSBcInN0YW5kYWxvbmVcIlxuY29uc3Qgcm91dGVNb2R1bGUgPSBuZXcgQXBwUm91dGVSb3V0ZU1vZHVsZSh7XG4gICAgZGVmaW5pdGlvbjoge1xuICAgICAgICBraW5kOiBSb3V0ZUtpbmQuQVBQX1JPVVRFLFxuICAgICAgICBwYWdlOiBcIi9hcGkvYXV0aC9bLi4ubmV4dGF1dGhdL3JvdXRlXCIsXG4gICAgICAgIHBhdGhuYW1lOiBcIi9hcGkvYXV0aC9bLi4ubmV4dGF1dGhdXCIsXG4gICAgICAgIGZpbGVuYW1lOiBcInJvdXRlXCIsXG4gICAgICAgIGJ1bmRsZVBhdGg6IFwiYXBwL2FwaS9hdXRoL1suLi5uZXh0YXV0aF0vcm91dGVcIlxuICAgIH0sXG4gICAgcmVzb2x2ZWRQYWdlUGF0aDogXCJDOlxcXFxVc2Vyc1xcXFxoc2FuYVxcXFx3YXFlZGlBxLBcXFxcZnJvbnRlbmRcXFxcd2ViLWNvbnNvbGVcXFxcYXBwXFxcXGFwaVxcXFxhdXRoXFxcXFsuLi5uZXh0YXV0aF1cXFxccm91dGUudHNcIixcbiAgICBuZXh0Q29uZmlnT3V0cHV0LFxuICAgIHVzZXJsYW5kXG59KTtcbi8vIFB1bGwgb3V0IHRoZSBleHBvcnRzIHRoYXQgd2UgbmVlZCB0byBleHBvc2UgZnJvbSB0aGUgbW9kdWxlLiBUaGlzIHNob3VsZFxuLy8gYmUgZWxpbWluYXRlZCB3aGVuIHdlJ3ZlIG1vdmVkIHRoZSBvdGhlciByb3V0ZXMgdG8gdGhlIG5ldyBmb3JtYXQuIFRoZXNlXG4vLyBhcmUgdXNlZCB0byBob29rIGludG8gdGhlIHJvdXRlLlxuY29uc3QgeyByZXF1ZXN0QXN5bmNTdG9yYWdlLCBzdGF0aWNHZW5lcmF0aW9uQXN5bmNTdG9yYWdlLCBzZXJ2ZXJIb29rcyB9ID0gcm91dGVNb2R1bGU7XG5jb25zdCBvcmlnaW5hbFBhdGhuYW1lID0gXCIvYXBpL2F1dGgvWy4uLm5leHRhdXRoXS9yb3V0ZVwiO1xuZnVuY3Rpb24gcGF0Y2hGZXRjaCgpIHtcbiAgICByZXR1cm4gX3BhdGNoRmV0Y2goe1xuICAgICAgICBzZXJ2ZXJIb29rcyxcbiAgICAgICAgc3RhdGljR2VuZXJhdGlvbkFzeW5jU3RvcmFnZVxuICAgIH0pO1xufVxuZXhwb3J0IHsgcm91dGVNb2R1bGUsIHJlcXVlc3RBc3luY1N0b3JhZ2UsIHN0YXRpY0dlbmVyYXRpb25Bc3luY1N0b3JhZ2UsIHNlcnZlckhvb2tzLCBvcmlnaW5hbFBhdGhuYW1lLCBwYXRjaEZldGNoLCAgfTtcblxuLy8jIHNvdXJjZU1hcHBpbmdVUkw9YXBwLXJvdXRlLmpzLm1hcCJdLCJuYW1lcyI6W10sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader.js?name=app%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute&page=%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute.ts&appDir=C%3A%5CUsers%5Chsana%5CwaqediA%C4%B0%5Cfrontend%5Cweb-console%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=C%3A%5CUsers%5Chsana%5CwaqediA%C4%B0%5Cfrontend%5Cweb-console&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!\n");

/***/ }),

/***/ "(rsc)/./app/api/auth/[...nextauth]/route.ts":
/*!*********************************************!*\
  !*** ./app/api/auth/[...nextauth]/route.ts ***!
  \*********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   GET: () => (/* binding */ handler),\n/* harmony export */   POST: () => (/* binding */ handler)\n/* harmony export */ });\n/* harmony import */ var next_auth__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next-auth */ \"(rsc)/./node_modules/next-auth/index.js\");\n/* harmony import */ var next_auth__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(next_auth__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var _core_auth_options__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @/core/auth-options */ \"(rsc)/./core/auth-options.ts\");\n/**\r\n * NextAuth API Route Handler\r\n */ \n\nconst handler = next_auth__WEBPACK_IMPORTED_MODULE_0___default()(_core_auth_options__WEBPACK_IMPORTED_MODULE_1__.authOptions);\n\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoiKHJzYykvLi9hcHAvYXBpL2F1dGgvWy4uLm5leHRhdXRoXS9yb3V0ZS50cyIsIm1hcHBpbmdzIjoiOzs7Ozs7OztBQUFBOztDQUVDLEdBRWdDO0FBQ2lCO0FBRWxELE1BQU1FLFVBQVVGLGdEQUFRQSxDQUFDQywyREFBV0E7QUFFTyIsInNvdXJjZXMiOlsid2VicGFjazovL3dhcWVkaS13ZWItY29uc29sZS8uL2FwcC9hcGkvYXV0aC9bLi4ubmV4dGF1dGhdL3JvdXRlLnRzP2M4YTQiXSwic291cmNlc0NvbnRlbnQiOlsiLyoqXHJcbiAqIE5leHRBdXRoIEFQSSBSb3V0ZSBIYW5kbGVyXHJcbiAqL1xyXG5cclxuaW1wb3J0IE5leHRBdXRoIGZyb20gJ25leHQtYXV0aCc7XHJcbmltcG9ydCB7IGF1dGhPcHRpb25zIH0gZnJvbSAnQC9jb3JlL2F1dGgtb3B0aW9ucyc7XHJcblxyXG5jb25zdCBoYW5kbGVyID0gTmV4dEF1dGgoYXV0aE9wdGlvbnMpO1xyXG5cclxuZXhwb3J0IHsgaGFuZGxlciBhcyBHRVQsIGhhbmRsZXIgYXMgUE9TVCB9O1xyXG4iXSwibmFtZXMiOlsiTmV4dEF1dGgiLCJhdXRoT3B0aW9ucyIsImhhbmRsZXIiLCJHRVQiLCJQT1NUIl0sInNvdXJjZVJvb3QiOiIifQ==\n//# sourceURL=webpack-internal:///(rsc)/./app/api/auth/[...nextauth]/route.ts\n");

/***/ }),

/***/ "(rsc)/./core/auth-options.ts":
/*!******************************!*\
  !*** ./core/auth-options.ts ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   authOptions: () => (/* binding */ authOptions)\n/* harmony export */ });\n/* harmony import */ var next_auth_providers_google__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! next-auth/providers/google */ \"(rsc)/./node_modules/next-auth/providers/google.js\");\n/**\r\n * NextAuth Configuration\r\n * \r\n * Enterprise OAuth setup with Google provider.\r\n * Extensible for future providers (GitHub, Microsoft).\r\n */ \nif (!process.env.GOOGLE_CLIENT_ID) {\n    throw new Error(\"Missing GOOGLE_CLIENT_ID environment variable\");\n}\nif (!process.env.GOOGLE_CLIENT_SECRET) {\n    throw new Error(\"Missing GOOGLE_CLIENT_SECRET environment variable\");\n}\nif (!process.env.NEXTAUTH_SECRET) {\n    throw new Error(\"Missing NEXTAUTH_SECRET environment variable\");\n}\nconst AUTH_API = \"http://localhost:8001\" || 0;\nconst authOptions = {\n    providers: [\n        (0,next_auth_providers_google__WEBPACK_IMPORTED_MODULE_0__[\"default\"])({\n            clientId: process.env.GOOGLE_CLIENT_ID,\n            clientSecret: process.env.GOOGLE_CLIENT_SECRET,\n            authorization: {\n                params: {\n                    prompt: \"consent\",\n                    access_type: \"offline\",\n                    response_type: \"code\"\n                }\n            }\n        })\n    ],\n    callbacks: {\n        async signIn ({ user, account, profile }) {\n            if (!account || !profile) return false;\n            // Only allow verified Google emails\n            if (account.provider === \"google\") {\n                const googleProfile = profile;\n                if (!googleProfile.email_verified) {\n                    return \"/login?error=email_not_verified\";\n                }\n            }\n            try {\n                // Send ID token to backend for verification and JWT issuance\n                const response = await fetch(`${AUTH_API}/auth/oauth/google`, {\n                    method: \"POST\",\n                    headers: {\n                        \"Content-Type\": \"application/json\"\n                    },\n                    body: JSON.stringify({\n                        id_token: account.id_token\n                    })\n                });\n                if (!response.ok) {\n                    const error = await response.json();\n                    console.error(\"Backend auth failed:\", error);\n                    return `/login?error=${error.detail || \"auth_failed\"}`;\n                }\n                const data = await response.json();\n                // Store backend tokens in account for session callback\n                account.backendAccessToken = data.access_token;\n                account.backendUserId = data.user_id;\n                account.isNewUser = data.is_new_user;\n                return true;\n            } catch (error) {\n                console.error(\"Auth error:\", error);\n                return \"/login?error=server_error\";\n            }\n        },\n        async jwt ({ token, account, user }) {\n            // On initial sign in, add backend tokens to JWT\n            if (account?.backendAccessToken) {\n                token.accessToken = account.backendAccessToken;\n                token.userId = account.backendUserId;\n                token.isNewUser = account.isNewUser;\n                token.provider = account.provider;\n            }\n            return token;\n        },\n        async session ({ session, token }) {\n            // Add backend tokens to session\n            return {\n                ...session,\n                accessToken: token.accessToken,\n                userId: token.userId,\n                isNewUser: token.isNewUser,\n                provider: token.provider\n            };\n        },\n        async redirect ({ url, baseUrl }) {\n            // Redirect to dashboard after login\n            if (url.startsWith(\"/\")) return `${baseUrl}${url}`;\n            if (new URL(url).origin === baseUrl) return url;\n            return baseUrl;\n        }\n    },\n    pages: {\n        signIn: \"/login\",\n        error: \"/login\"\n    },\n    session: {\n        strategy: \"jwt\",\n        maxAge: 24 * 60 * 60\n    },\n    secret: process.env.NEXTAUTH_SECRET,\n    debug: \"development\" === \"development\"\n};\n//# sourceURL=[module]\n//# sourceMappingURL=data:application/json;charset=utf-8;base64,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Z0JBQzFCckIsVUFBVXdCLE1BQU14QixRQUFRO1lBQzVCO1FBQ0o7UUFFQSxNQUFNNEIsVUFBUyxFQUFFQyxHQUFHLEVBQUVDLE9BQU8sRUFBRTtZQUMzQixvQ0FBb0M7WUFDcEMsSUFBSUQsSUFBSUUsVUFBVSxDQUFDLE1BQU0sT0FBTyxDQUFDLEVBQUVELFFBQVEsRUFBRUQsSUFBSSxDQUFDO1lBQ2xELElBQUksSUFBSUcsSUFBSUgsS0FBS0ksTUFBTSxLQUFLSCxTQUFTLE9BQU9EO1lBQzVDLE9BQU9DO1FBQ1g7SUFDSjtJQUVBSSxPQUFPO1FBQ0h0QyxRQUFRO1FBQ1JnQixPQUFPO0lBQ1g7SUFFQWUsU0FBUztRQUNMUSxVQUFVO1FBQ1ZDLFFBQVEsS0FBSyxLQUFLO0lBQ3RCO0lBRUFDLFFBQVEzRCxRQUFRQyxHQUFHLENBQUNJLGVBQWU7SUFFbkN1RCxPQUFPNUQsa0JBQXlCO0FBQ3BDLEVBQUUiLCJzb3VyY2VzIjpbIndlYnBhY2s6Ly93YXFlZGktd2ViLWNvbnNvbGUvLi9jb3JlL2F1dGgtb3B0aW9ucy50cz9jMDVkIl0sInNvdXJjZXNDb250ZW50IjpbIi8qKlxyXG4gKiBOZXh0QXV0aCBDb25maWd1cmF0aW9uXHJcbiAqIFxyXG4gKiBFbnRlcnByaXNlIE9BdXRoIHNldHVwIHdpdGggR29vZ2xlIHByb3ZpZGVyLlxyXG4gKiBFeHRlbnNpYmxlIGZvciBmdXR1cmUgcHJvdmlkZXJzIChHaXRIdWIsIE1pY3Jvc29mdCkuXHJcbiAqL1xyXG5cclxuaW1wb3J0IHsgQXV0aE9wdGlvbnMgfSBmcm9tICduZXh0LWF1dGgnO1xyXG5pbXBvcnQgR29vZ2xlUHJvdmlkZXIgZnJvbSAnbmV4dC1hdXRoL3Byb3ZpZGVycy9nb29nbGUnO1xyXG5cclxuaWYgKCFwcm9jZXNzLmVudi5HT09HTEVfQ0xJRU5UX0lEKSB7XHJcbiAgICB0aHJvdyBuZXcgRXJyb3IoJ01pc3NpbmcgR09PR0xFX0NMSUVOVF9JRCBlbnZpcm9ubWVudCB2YXJpYWJsZScpO1xyXG59XHJcblxyXG5pZiAoIXByb2Nlc3MuZW52LkdPT0dMRV9DTElFTlRfU0VDUkVUKSB7XHJcbiAgICB0aHJvdyBuZXcgRXJyb3IoJ01pc3NpbmcgR09PR0xFX0NMSUVOVF9TRUNSRVQgZW52aXJvbm1lbnQgdmFyaWFibGUnKTtcclxufVxyXG5cclxuaWYgKCFwcm9jZXNzLmVudi5ORVhUQVVUSF9TRUNSRVQpIHtcclxuICAgIHRocm93IG5ldyBFcnJvcignTWlzc2luZyBORVhUQVVUSF9TRUNSRVQgZW52aXJvbm1lbnQgdmFyaWFibGUnKTtcclxufVxyXG5cclxuY29uc3QgQVVUSF9BUEkgPSBwcm9jZXNzLmVudi5ORVhUX1BVQkxJQ19BVVRIX0FQSSB8fCAnaHR0cDovL2xvY2FsaG9zdDo4MDAxJztcclxuXHJcbmV4cG9ydCBjb25zdCBhdXRoT3B0aW9uczogQXV0aE9wdGlvbnMgPSB7XHJcbiAgICBwcm92aWRlcnM6IFtcclxuICAgICAgICBHb29nbGVQcm92aWRlcih7XHJcbiAgICAgICAgICAgIGNsaWVudElkOiBwcm9jZXNzLmVudi5HT09HTEVfQ0xJRU5UX0lELFxyXG4gICAgICAgICAgICBjbGllbnRTZWNyZXQ6IHByb2Nlc3MuZW52LkdPT0dMRV9DTElFTlRfU0VDUkVULFxyXG4gICAgICAgICAgICBhdXRob3JpemF0aW9uOiB7XHJcbiAgICAgICAgICAgICAgICBwYXJhbXM6IHtcclxuICAgICAgICAgICAgICAgICAgICBwcm9tcHQ6ICdjb25zZW50JyxcclxuICAgICAgICAgICAgICAgICAgICBhY2Nlc3NfdHlwZTogJ29mZmxpbmUnLFxyXG4gICAgICAgICAgICAgICAgICAgIHJlc3BvbnNlX3R5cGU6ICdjb2RlJyxcclxuICAgICAgICAgICAgICAgIH0sXHJcbiAgICAgICAgICAgIH0sXHJcbiAgICAgICAgfSksXHJcbiAgICAgICAgLy8gRnV0dXJlIHByb3ZpZGVycyBjYW4gYmUgYWRkZWQgaGVyZTpcclxuICAgICAgICAvLyBHaXRIdWJQcm92aWRlcih7IC4uLiB9KSxcclxuICAgICAgICAvLyBBenVyZUFEUHJvdmlkZXIoeyAuLi4gfSksXHJcbiAgICBdLFxyXG5cclxuICAgIGNhbGxiYWNrczoge1xyXG4gICAgICAgIGFzeW5jIHNpZ25Jbih7IHVzZXIsIGFjY291bnQsIHByb2ZpbGUgfSkge1xyXG4gICAgICAgICAgICBpZiAoIWFjY291bnQgfHwgIXByb2ZpbGUpIHJldHVybiBmYWxzZTtcclxuXHJcbiAgICAgICAgICAgIC8vIE9ubHkgYWxsb3cgdmVyaWZpZWQgR29vZ2xlIGVtYWlsc1xyXG4gICAgICAgICAgICBpZiAoYWNjb3VudC5wcm92aWRlciA9PT0gJ2dvb2dsZScpIHtcclxuICAgICAgICAgICAgICAgIGNvbnN0IGdvb2dsZVByb2ZpbGUgPSBwcm9maWxlIGFzIHsgZW1haWxfdmVyaWZpZWQ/OiBib29sZWFuIH07XHJcbiAgICAgICAgICAgICAgICBpZiAoIWdvb2dsZVByb2ZpbGUuZW1haWxfdmVyaWZpZWQpIHtcclxuICAgICAgICAgICAgICAgICAgICByZXR1cm4gJy9sb2dpbj9lcnJvcj1lbWFpbF9ub3RfdmVyaWZpZWQnO1xyXG4gICAgICAgICAgICAgICAgfVxyXG4gICAgICAgICAgICB9XHJcblxyXG4gICAgICAgICAgICB0cnkge1xyXG4gICAgICAgICAgICAgICAgLy8gU2VuZCBJRCB0b2tlbiB0byBiYWNrZW5kIGZvciB2ZXJpZmljYXRpb24gYW5kIEpXVCBpc3N1YW5jZVxyXG4gICAgICAgICAgICAgICAgY29uc3QgcmVzcG9uc2UgPSBhd2FpdCBmZXRjaChgJHtBVVRIX0FQSX0vYXV0aC9vYXV0aC9nb29nbGVgLCB7XHJcbiAgICAgICAgICAgICAgICAgICAgbWV0aG9kOiAnUE9TVCcsXHJcbiAgICAgICAgICAgICAgICAgICAgaGVhZGVyczogeyAnQ29udGVudC1UeXBlJzogJ2FwcGxpY2F0aW9uL2pzb24nIH0sXHJcbiAgICAgICAgICAgICAgICAgICAgYm9keTogSlNPTi5zdHJpbmdpZnkoe1xyXG4gICAgICAgICAgICAgICAgICAgICAgICBpZF90b2tlbjogYWNjb3VudC5pZF90b2tlbixcclxuICAgICAgICAgICAgICAgICAgICB9KSxcclxuICAgICAgICAgICAgICAgIH0pO1xyXG5cclxuICAgICAgICAgICAgICAgIGlmICghcmVzcG9uc2Uub2spIHtcclxuICAgICAgICAgICAgICAgICAgICBjb25zdCBlcnJvciA9IGF3YWl0IHJlc3BvbnNlLmpzb24oKTtcclxuICAgICAgICAgICAgICAgICAgICBjb25zb2xlLmVycm9yKCdCYWNrZW5kIGF1dGggZmFpbGVkOicsIGVycm9yKTtcclxuICAgICAgICAgICAgICAgICAgICByZXR1cm4gYC9sb2dpbj9lcnJvcj0ke2Vycm9yLmRldGFpbCB8fCAnYXV0aF9mYWlsZWQnfWA7XHJcbiAgICAgICAgICAgICAgICB9XHJcblxyXG4gICAgICAgICAgICAgICAgY29uc3QgZGF0YSA9IGF3YWl0IHJlc3BvbnNlLmpzb24oKTtcclxuXHJcbiAgICAgICAgICAgICAgICAvLyBTdG9yZSBiYWNrZW5kIHRva2VucyBpbiBhY2NvdW50IGZvciBzZXNzaW9uIGNhbGxiYWNrXHJcbiAgICAgICAgICAgICAgICBhY2NvdW50LmJhY2tlbmRBY2Nlc3NUb2tlbiA9IGRhdGEuYWNjZXNzX3Rva2VuO1xyXG4gICAgICAgICAgICAgICAgYWNjb3VudC5iYWNrZW5kVXNlcklkID0gZGF0YS51c2VyX2lkO1xyXG4gICAgICAgICAgICAgICAgYWNjb3VudC5pc05ld1VzZXIgPSBkYXRhLmlzX25ld191c2VyO1xyXG5cclxuICAgICAgICAgICAgICAgIHJldHVybiB0cnVlO1xyXG4gICAgICAgICAgICB9IGNhdGNoIChlcnJvcikge1xyXG4gICAgICAgICAgICAgICAgY29uc29sZS5lcnJvcignQXV0aCBlcnJvcjonLCBlcnJvcik7XHJcbiAgICAgICAgICAgICAgICByZXR1cm4gJy9sb2dpbj9lcnJvcj1zZXJ2ZXJfZXJyb3InO1xyXG4gICAgICAgICAgICB9XHJcbiAgICAgICAgfSxcclxuXHJcbiAgICAgICAgYXN5bmMgand0KHsgdG9rZW4sIGFjY291bnQsIHVzZXIgfSkge1xyXG4gICAgICAgICAgICAvLyBPbiBpbml0aWFsIHNpZ24gaW4sIGFkZCBiYWNrZW5kIHRva2VucyB0byBKV1RcclxuICAgICAgICAgICAgaWYgKGFjY291bnQ/LmJhY2tlbmRBY2Nlc3NUb2tlbikge1xyXG4gICAgICAgICAgICAgICAgdG9rZW4uYWNjZXNzVG9rZW4gPSBhY2NvdW50LmJhY2tlbmRBY2Nlc3NUb2tlbjtcclxuICAgICAgICAgICAgICAgIHRva2VuLnVzZXJJZCA9IGFjY291bnQuYmFja2VuZFVzZXJJZDtcclxuICAgICAgICAgICAgICAgIHRva2VuLmlzTmV3VXNlciA9IGFjY291bnQuaXNOZXdVc2VyO1xyXG4gICAgICAgICAgICAgICAgdG9rZW4ucHJvdmlkZXIgPSBhY2NvdW50LnByb3ZpZGVyO1xyXG4gICAgICAgICAgICB9XHJcbiAgICAgICAgICAgIHJldHVybiB0b2tlbjtcclxuICAgICAgICB9LFxyXG5cclxuICAgICAgICBhc3luYyBzZXNzaW9uKHsgc2Vzc2lvbiwgdG9rZW4gfSkge1xyXG4gICAgICAgICAgICAvLyBBZGQgYmFja2VuZCB0b2tlbnMgdG8gc2Vzc2lvblxyXG4gICAgICAgICAgICByZXR1cm4ge1xyXG4gICAgICAgICAgICAgICAgLi4uc2Vzc2lvbixcclxuICAgICAgICAgICAgICAgIGFjY2Vzc1Rva2VuOiB0b2tlbi5hY2Nlc3NUb2tlbiBhcyBzdHJpbmcsXHJcbiAgICAgICAgICAgICAgICB1c2VySWQ6IHRva2VuLnVzZXJJZCBhcyBzdHJpbmcsXHJcbiAgICAgICAgICAgICAgICBpc05ld1VzZXI6IHRva2VuLmlzTmV3VXNlciBhcyBib29sZWFuLFxyXG4gICAgICAgICAgICAgICAgcHJvdmlkZXI6IHRva2VuLnByb3ZpZGVyIGFzIHN0cmluZyxcclxuICAgICAgICAgICAgfTtcclxuICAgICAgICB9LFxyXG5cclxuICAgICAgICBhc3luYyByZWRpcmVjdCh7IHVybCwgYmFzZVVybCB9KSB7XHJcbiAgICAgICAgICAgIC8vIFJlZGlyZWN0IHRvIGRhc2hib2FyZCBhZnRlciBsb2dpblxyXG4gICAgICAgICAgICBpZiAodXJsLnN0YXJ0c1dpdGgoJy8nKSkgcmV0dXJuIGAke2Jhc2VVcmx9JHt1cmx9YDtcclxuICAgICAgICAgICAgaWYgKG5ldyBVUkwodXJsKS5vcmlnaW4gPT09IGJhc2VVcmwpIHJldHVybiB1cmw7XHJcbiAgICAgICAgICAgIHJldHVybiBiYXNlVXJsO1xyXG4gICAgICAgIH0sXHJcbiAgICB9LFxyXG5cclxuICAgIHBhZ2VzOiB7XHJcbiAgICAgICAgc2lnbkluOiAnL2xvZ2luJyxcclxuICAgICAgICBlcnJvcjogJy9sb2dpbicsXHJcbiAgICB9LFxyXG5cclxuICAgIHNlc3Npb246IHtcclxuICAgICAgICBzdHJhdGVneTogJ2p3dCcsXHJcbiAgICAgICAgbWF4QWdlOiAyNCAqIDYwICogNjAsIC8vIDI0IGhvdXJzXHJcbiAgICB9LFxyXG5cclxuICAgIHNlY3JldDogcHJvY2Vzcy5lbnYuTkVYVEFVVEhfU0VDUkVULFxyXG5cclxuICAgIGRlYnVnOiBwcm9jZXNzLmVudi5OT0RFX0VOViA9PT0gJ2RldmVsb3BtZW50JyxcclxufTtcclxuIl0sIm5hbWVzIjpbIkdvb2dsZVByb3ZpZGVyIiwicHJvY2VzcyIsImVudiIsIkdPT0dMRV9DTElFTlRfSUQiLCJFcnJvciIsIkdPT0dMRV9DTElFTlRfU0VDUkVUIiwiTkVYVEFVVEhfU0VDUkVUIiwiQVVUSF9BUEkiLCJORVhUX1BVQkxJQ19BVVRIX0FQSSIsImF1dGhPcHRpb25zIiwicHJvdmlkZXJzIiwiY2xpZW50SWQiLCJjbGllbnRTZWNyZXQiLCJhdXRob3JpemF0aW9uIiwicGFyYW1zIiwicHJvbXB0IiwiYWNjZXNzX3R5cGUiLCJyZXNwb25zZV90eXBlIiwiY2FsbGJhY2tzIiwic2lnbkluIiwidXNlciIsImFjY291bnQiLCJwcm9maWxlIiwicHJvdmlkZXIiLCJnb29nbGVQcm9maWxlIiwiZW1haWxfdmVyaWZpZWQiLCJyZXNwb25zZSIsImZldGNoIiwibWV0aG9kIiwiaGVhZGVycyIsImJvZHkiLCJKU09OIiwic3RyaW5naWZ5IiwiaWRfdG9rZW4iLCJvayIsImVycm9yIiwianNvbiIsImNvbnNvbGUiLCJkZXRhaWwiLCJkYXRhIiwiYmFja2VuZEFjY2Vzc1Rva2VuIiwiYWNjZXNzX3Rva2VuIiwiYmFja2VuZFVzZXJJZCIsInVzZXJfaWQiLCJpc05ld1VzZXIiLCJpc19uZXdfdXNlciIsImp3dCIsInRva2VuIiwiYWNjZXNzVG9rZW4iLCJ1c2VySWQiLCJzZXNzaW9uIiwicmVkaXJlY3QiLCJ1cmwiLCJiYXNlVXJsIiwic3RhcnRzV2l0aCIsIlVSTCIsIm9yaWdpbiIsInBhZ2VzIiwic3RyYXRlZ3kiLCJtYXhBZ2UiLCJzZWNyZXQiLCJkZWJ1ZyJdLCJzb3VyY2VSb290IjoiIn0=\n//# sourceURL=webpack-internal:///(rsc)/./core/auth-options.ts\n");

/***/ })

};
;

// load runtime
var __webpack_require__ = require("../../../../webpack-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = __webpack_require__.X(0, ["vendor-chunks/next","vendor-chunks/next-auth","vendor-chunks/@babel","vendor-chunks/jose","vendor-chunks/openid-client","vendor-chunks/uuid","vendor-chunks/oauth","vendor-chunks/@panva","vendor-chunks/yallist","vendor-chunks/preact-render-to-string","vendor-chunks/preact","vendor-chunks/oidc-token-hash","vendor-chunks/cookie"], () => (__webpack_exec__("(rsc)/./node_modules/next/dist/build/webpack/loaders/next-app-loader.js?name=app%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute&page=%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute&appPaths=&pagePath=private-next-app-dir%2Fapi%2Fauth%2F%5B...nextauth%5D%2Froute.ts&appDir=C%3A%5CUsers%5Chsana%5CwaqediA%C4%B0%5Cfrontend%5Cweb-console%5Capp&pageExtensions=tsx&pageExtensions=ts&pageExtensions=jsx&pageExtensions=js&rootDir=C%3A%5CUsers%5Chsana%5CwaqediA%C4%B0%5Cfrontend%5Cweb-console&isDev=true&tsconfigPath=tsconfig.json&basePath=&assetPrefix=&nextConfigOutput=standalone&preferredRegion=&middlewareConfig=e30%3D!")));
module.exports = __webpack_exports__;

})();