(() => {
  const selects = document.querySelectorAll('.language-select');
  const nodes = document.querySelectorAll('[data-en][data-sw]');
  let language = 'en';
  try { language = localStorage.getItem('orca-language') === 'sw' ? 'sw' : 'en'; } catch (_) {}
  const swErrors = {
    "An account with this email already exists.": "Akaunti yenye barua pepe hii tayari ipo.",
    "An account with this phone number already exists.": "Akaunti yenye namba hii ya simu tayari ipo.",
    "The passwords do not match.": "Nenosiri halifanani.",
    "Email or password is incorrect.": "Barua pepe au nenosiri si sahihi.",
    "This account is inactive.": "Akaunti hii haijawashwa.",
    "Administrators may create customer service accounts only.": "Wasimamizi wanaweza kufungua akaunti za huduma kwa wateja pekee."
  };
  const roleNames = { customer_service: "Huduma kwa wateja", customer: "Mteja", admin: "Msimamizi", finance: "Fedha", partner_viewer: "Mwakilishi wa mshirika", support: "Usaidizi", superuser: "Msimamizi mkuu" };
  function apply(next) {
    language = next === 'sw' ? 'sw' : 'en';
    document.documentElement.lang = language;
    nodes.forEach(node => { node.textContent = node.dataset[language]; });
    document.querySelectorAll('.errorlist li').forEach(node => {
      const source = node.dataset.en || node.textContent.trim();
      node.dataset.en = source;
      node.textContent = language === 'sw' ? (swErrors[source] || source) : source;
    });
    const roleLabels = { customer_service: "Customer service", customer: "Customer", admin: "Administrator", finance: "Finance", partner_viewer: "Partner viewer", support: "Support", superuser: "Superuser" };
    const roleSelect = document.getElementById('id_role');
    if (roleSelect) Array.from(roleSelect.options).forEach(option => {
      const english = option.dataset.en || option.textContent;
      option.dataset.en = english;
      option.textContent = language === 'sw' ? (roleNames[option.value] || english) : english;
    });
    document.querySelectorAll('.role-display').forEach(node => {
      const role = node.dataset.role;
      const english = roleLabels[role] || node.textContent;
      const swahili = roleNames[role] || english;
      node.textContent = language === 'sw' ? swahili : english;
    });
    selects.forEach(select => { select.value = language; });
    try { localStorage.setItem('orca-language', language); } catch (_) {}
  }
  selects.forEach(select => select.addEventListener('change', () => apply(select.value)));
  apply(language);
})();
