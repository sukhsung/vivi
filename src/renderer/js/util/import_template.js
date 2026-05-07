export async function import_template(path) {
  var template = document.createElement("template");
  template.innerHTML = await (await fetch(path)).text();
  return template;
}
