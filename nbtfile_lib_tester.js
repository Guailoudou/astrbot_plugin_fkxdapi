import { NBTFILE_PARSER, NBTFILE_SAVER, MCNBT } from "./nbtfile_lib.js";
import { writeFileSync } from "fs";
let tester = new NBTFILE_PARSER();

tester.try_load_file_with_gzip("./scoreboard.dat");

let res = tester.parse();

writeFileSync("./scoreboard.json", JSON.stringify(res, null, 2));