"""Read-only canonical serialization; provider association is a separate gate."""

PROMPT_CHIP_SERIALIZER_JS = r"""(el => {
  const raw = el.innerText || '';
  const chips = [];
  const fail = reason => { throw new Error(reason); };
  const children = n => Array.from(n.childNodes);
  const attr = (n, key) => n.getAttribute(key);
  const tag = (n, name) => n.nodeType === 1 && n.tagName === name;
  const textOnly = n => {
    if (!children(n).every(c => c.nodeType === 3)) fail('UNKNOWN_TEXT_STRUCTURE');
    return children(n).map(c => c.nodeValue).join('');
  };
  const inline = n => {
    if (n.nodeType === 3) return n.nodeValue;
    if (tag(n, 'BR') && children(n).length === 0) return '\n';
    if (!tag(n, 'SPAN')) fail('UNKNOWN_INLINE_STRUCTURE');
    if (attr(n, 'data-reference') !== null) {
      const m = /^@Image ([1-9][0-9]*)$/.exec(attr(n, 'data-reference'));
      const id = attr(n, 'data-asset-id');
      if (!m || !id || !/^[a-zA-Z0-9-]+$/.test(id) ||
          id !== attr(n, 'data-reference-id') ||
          attr(n, 'data-lexical-decorator') !== 'true' ||
          attr(n, 'contenteditable') !== 'false') fail('INVALID_CHIP_IDENTITY');
      const cs = children(n), label = 'Image ' + m[1];
      if (cs.length !== 1 || !tag(cs[0], 'BUTTON') ||
          attr(cs[0], 'aria-label') !== 'View ' + label + ' larger') fail('INVALID_CHIP_BUTTON');
      const bs = children(cs[0]);
      if (bs.length !== 2 || !tag(bs[0], 'IMG') || children(bs[0]).length ||
          !tag(bs[1], 'SPAN') || textOnly(bs[1]) !== label) fail('UNKNOWN_CHIP_STRUCTURE');
      const token = '@Image' + m[1];
      if (chips.some(c => c.token === token || c.provider_asset_id === id)) fail('DUPLICATE_CHIP');
      chips.push({token, provider_asset_id:id, provider_reference_id:id});
      return token;
    }
    if (attr(n, 'data-lexical-text') !== 'true' ||
        attr(n, 'data-asset-id') !== null || attr(n, 'data-reference-id') !== null ||
        attr(n, 'data-lexical-decorator') !== null) fail('UNKNOWN_SPAN_STRUCTURE');
    return textOnly(n);
  };
  try {
    const ps = children(el);
    if (!ps.every(p => tag(p, 'P'))) fail('UNKNOWN_PARAGRAPH_STRUCTURE');
    const text = ps.map(p => {
      const ns = children(p);
      return ns.length === 1 && tag(ns[0], 'BR') && !children(ns[0]).length
        ? '' : ns.map(inline).join('');
    }).join('\n');
    return {ok:true, text, raw_display_text:raw, chips,
      serialization_version:'runway_image_chip_v1', asset_binding_verified:false};
  } catch (e) {
    return {ok:false, error:e.message, raw_display_text:raw, chips,
      serialization_version:'runway_image_chip_v1', asset_binding_verified:false};
  }
})"""
