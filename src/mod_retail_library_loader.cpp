/*
 * mod-retail-library loader.
 *
 * The module is data only: world database rows (data/sql/db-world) that tell the server about the
 * creature displays in the client patches. AzerothCore still calls a loader for every module
 * folder, so this one is empty.
 *
 * AzerothCore looks up a loader symbol derived from the module's folder name: for folder
 * "mod-retail-library" that symbol is exactly "Addmod_retail_libraryScripts". If you clone the repo
 * under a different folder name, rename this function to match.
 *
 * Released under the MIT License.
 */

void Addmod_retail_libraryScripts()
{
}
