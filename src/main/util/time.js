export function get_timestamp() {
  const d = new Date();
  const iso = localISOTime( d )
  const count = d.getTime()

  return {timestamp:count, local_iso:iso}
}

function localISOTime( d ) {
    // d Date object (e.g., d = new Date())
  const pad = (n, z = 2) => String(n).padStart(z, '0');
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} `
       + `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}.`+
    `${pad(d.getMilliseconds(), 3)}`;
}
