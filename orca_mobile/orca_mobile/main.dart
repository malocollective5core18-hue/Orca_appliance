// ORCA mobile app (demo) - single-file Flutter main.dart
//
// Screens: Home, Pay, Device, History + Link TV.
// Demo only: sample data, no real payments and no real TV control.
//
// Setup (pubspec.yaml):
//   flutter:
//     assets:
//       - assets/orca-logo-w.png   # white dots (used in dark theme)
//       - assets/orca-logo-B.png   # black dots (used in light theme)
// If the images are missing the app shows a simple circle instead.
// No extra packages are needed.

import 'dart:math' as math;
import 'dart:ui' show FontFeature;
import 'package:flutter/material.dart';

void main() => runApp(const OrcaApp());

/// Set to your font family name after adding it to pubspec.yaml
/// (for example 'SpaceGrotesk'). null uses the platform default.
const String? kFont = null;

// ---------------------------------------------------------------- helpers

String fmt(int n) => n
    .toString()
    .replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (m) => ',');

const _tabular = [FontFeature.tabularFigures()];

String applyKey(String d, String k, int maxLen) {
  if (k == '⌫') return d.isEmpty ? d : d.substring(0, d.length - 1);
  var n = (d + k).replaceFirst(RegExp(r'^0+'), '');
  return n.length > maxLen ? d : n;
}

void toast(BuildContext c, String m) {
  final inset = MediaQuery.of(c).padding.bottom;
  ScaffoldMessenger.of(c)
    ..hideCurrentSnackBar()
    ..showSnackBar(SnackBar(
      content: Text(m),
      behavior: SnackBarBehavior.floating,
      margin: EdgeInsets.fromLTRB(16, 0, 16, 84 + inset),
    ));
}

// ---------------------------------------------------------------- design tokens

class Tk {
  final Color bg, surface, surface2, text, muted, line, field, ok, err;
  final Color card, ctext, cmuted, cline;
  final List<BoxShadow> sh;
  const Tk({
    required this.bg,
    required this.surface,
    required this.surface2,
    required this.text,
    required this.muted,
    required this.line,
    required this.field,
    required this.ok,
    required this.err,
    required this.card,
    required this.ctext,
    required this.cmuted,
    required this.cline,
    required this.sh,
  });

  static const red = Color(0xFFD71921);

  static const dark = Tk(
    bg: Color(0xFF0D0D0D),
    surface: Color(0xFF171717),
    surface2: Color(0xFF242424),
    text: Color(0xFFF2F2F0),
    muted: Color(0xFF8F8F8B),
    line: Color(0xFF2E2E2E),
    field: Color(0xFF6F6F6B),
    ok: Color(0xFF5FD08B),
    err: Color(0xFFFF7A7A),
    card: Color(0xFFF4F4F2),
    ctext: Color(0xFF0D0D0D),
    cmuted: Color(0xFF5A5A56),
    cline: Color(0xFFBDBDB8),
    sh: [
      BoxShadow(color: Color(0x80000000), blurRadius: 2, offset: Offset(0, 1)),
      BoxShadow(color: Color(0x4D000000), blurRadius: 14, offset: Offset(0, 6)),
    ],
  );

  static const light = Tk(
    bg: Color(0xFFF6F6F4),
    surface: Color(0xFFFFFFFF),
    surface2: Color(0xFFEBEBE8),
    text: Color(0xFF111111),
    muted: Color(0xFF5A5A56),
    line: Color(0xFFD6D6D2),
    field: Color(0xFF85857F),
    ok: Color(0xFF0F7A3D),
    err: Color(0xFFB3121A),
    card: Color(0xFF111111),
    ctext: Color(0xFFF2F2F0),
    cmuted: Color(0xFFA8A8A4),
    cline: Color(0xFF333333),
    sh: [
      BoxShadow(color: Color(0x0D111111), blurRadius: 2, offset: Offset(0, 1)),
      BoxShadow(color: Color(0x0D111111), blurRadius: 12, offset: Offset(0, 4)),
    ],
  );
}

Tk tk(BuildContext c) =>
    Theme.of(c).brightness == Brightness.dark ? Tk.dark : Tk.light;

// ---------------------------------------------------------------- state

class Tx {
  final String name, when, sub;
  final int amount;
  const Tx(this.name, this.when, this.sub, this.amount);
}

class AppState extends ChangeNotifier {
  static const deviceName = 'Hisense 55" Smart TV';
  static const category = 'Smart TV';
  static const total = 1200000;
  static const monthly = 100000;
  static const nextDue = '28 Oct';

  int due = 38000;
  int paid = 462000;
  bool restricted = false;
  bool tvLinked = false;
  bool hide = false;
  int tab = 0;
  String draft = '';
  List<Tx> txs = _seed();

  static List<Tx> _seed() => [
        const Tx('Installment', '5 Oct', 'Sample · M-Pesa', 62000),
        const Tx('Installment', '12 Sep', 'Sample · M-Pesa', 100000),
        const Tx('Installment', '12 Aug', 'Sample · Bank transfer', 100000),
        const Tx('Installment', '12 Jul', 'Sample · M-Pesa', 100000),
        const Tx('Installment', '12 Jun', 'Sample · M-Pesa', 100000),
      ];

  int get remaining => total - paid;
  int get pct => paid * 100 ~/ total;
  int get left => (remaining / monthly).ceil();

  void go(int t) {
    tab = t;
    notifyListeners();
  }

  void setDraft(String d) {
    draft = d;
    notifyListeners();
  }

  void toggleHide() {
    hide = !hide;
    notifyListeners();
  }

  void pay(int n, String method) {
    paid += n;
    due = math.max(0, due - n);
    if (due == 0) restricted = false; // demo only: real status comes from ORCA Cloud
    txs.insert(0, Tx('Installment', 'Just now', 'Demo · $method', n));
    notifyListeners();
  }

  void toggleRestricted() {
    restricted = !restricted;
    notifyListeners();
  }

  void linkTv() {
    tvLinked = true;
    notifyListeners();
  }

  void reset() {
    due = 38000;
    paid = 462000;
    restricted = false;
    tvLinked = false;
    draft = '';
    txs = _seed();
    notifyListeners();
  }
}

// ---------------------------------------------------------------- app

class OrcaApp extends StatefulWidget {
  const OrcaApp({super.key});
  @override
  State<OrcaApp> createState() => _OrcaAppState();
}

class _OrcaAppState extends State<OrcaApp> {
  final AppState state = AppState();
  ThemeMode mode = ThemeMode.system;

  void toggleTheme(Brightness current) => setState(() => mode =
      current == Brightness.dark ? ThemeMode.light : ThemeMode.dark);

  ThemeData _theme(Brightness b) {
    final t = b == Brightness.dark ? Tk.dark : Tk.light;
    return ThemeData(
      useMaterial3: true,
      brightness: b,
      fontFamily: kFont,
      scaffoldBackgroundColor: t.bg,
      colorScheme: ColorScheme.fromSeed(seedColor: Tk.red, brightness: b)
          .copyWith(primary: Tk.red, surface: t.surface),
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'ORCA',
      themeMode: mode,
      theme: _theme(Brightness.light),
      darkTheme: _theme(Brightness.dark),
      home: Shell(state: state, onTheme: toggleTheme),
    );
  }
}

// ---------------------------------------------------------------- shell

class Shell extends StatelessWidget {
  final AppState state;
  final void Function(Brightness) onTheme;
  const Shell({super.key, required this.state, required this.onTheme});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: state,
      builder: (context, _) {
        final t = tk(context);
        final inset = MediaQuery.of(context).padding.bottom;
        return Scaffold(
          backgroundColor: t.bg,
          body: SafeArea(
            bottom: false,
            child: Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 480),
                child: Stack(children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                    child: Column(children: [
                      _Header(state: state, onTheme: onTheme),
                      const SizedBox(height: 6),
                      const _DemoBanner(),
                      const SizedBox(height: 8),
                      Expanded(
                        child: Padding(
                          padding: EdgeInsets.only(bottom: 78 + inset),
                          child: IndexedStack(index: state.tab, children: [
                            HomeTab(state: state),
                            PayTab(state: state),
                            DeviceTab(state: state),
                            HistoryTab(state: state),
                          ]),
                        ),
                      ),
                    ]),
                  ),
                  Positioned(
                    left: 0,
                    right: 0,
                    bottom: 14 + inset,
                    child: Center(child: _NavPill(state: state)),
                  ),
                ]),
              ),
            ),
          ),
        );
      },
    );
  }
}

class _Logo extends StatelessWidget {
  final double size;
  const _Logo(this.size);
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Image.asset(
      dark ? 'assets/orca-logo-w.png' : 'assets/orca-logo-B.png',
      width: size,
      height: size,
      semanticLabel: 'ORCA',
      errorBuilder: (c, e, s) => Container(
        width: size,
        height: size,
        alignment: Alignment.center,
        decoration:
            BoxDecoration(shape: BoxShape.circle, border: Border.all(color: t.text)),
        child: Text('O', style: TextStyle(color: t.text, fontWeight: FontWeight.w600)),
      ),
    );
  }
}

class _Pill extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const _Pill(this.label, this.onTap);
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return Semantics(
      button: true,
      label: label,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(99),
        child: Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 14),
          alignment: Alignment.center,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(99),
            border: Border.all(color: t.field),
          ),
          child: Text(label, style: TextStyle(fontSize: 12, color: t.text)),
        ),
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final AppState state;
  final void Function(Brightness) onTheme;
  const _Header({required this.state, required this.onTheme});
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    final b = Theme.of(context).brightness;
    return Row(children: [
      const _Logo(44),
      const SizedBox(width: 10),
      Expanded(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('ORCA · Good day', style: TextStyle(fontSize: 12, color: t.muted)),
          Text('Amina',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w500, color: t.text)),
        ]),
      ),
      _Pill(state.hide ? 'Show amount' : 'Hide amount', state.toggleHide),
      const SizedBox(width: 6),
      _Pill(b == Brightness.dark ? 'Light' : 'Dark', () => onTheme(b)),
    ]);
  }
}

class _DemoBanner extends StatelessWidget {
  const _DemoBanner();
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(color: t.surface, borderRadius: BorderRadius.circular(10)),
      child: Row(children: [
        Container(
            width: 6,
            height: 6,
            decoration: const BoxDecoration(color: Tk.red, shape: BoxShape.circle)),
        const SizedBox(width: 8),
        Expanded(
          child: Text('Demo mode: no real money moves, no device is controlled.',
              style: TextStyle(fontSize: 12, color: t.muted)),
        ),
      ]),
    );
  }
}

class _NavPill extends StatelessWidget {
  final AppState state;
  const _NavPill({required this.state});
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    const labels = ['Home', 'Pay', 'Device', 'History'];
    return Container(
      padding: const EdgeInsets.all(5),
      decoration: BoxDecoration(
          color: t.text, borderRadius: BorderRadius.circular(99), boxShadow: t.sh),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        for (var i = 0; i < labels.length; i++)
          Semantics(
            button: true,
            selected: state.tab == i,
            label: labels[i],
            child: InkWell(
              onTap: () => state.go(i),
              borderRadius: BorderRadius.circular(99),
              child: Container(
                width: 76,
                height: 44,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: state.tab == i ? t.bg : Colors.transparent,
                  borderRadius: BorderRadius.circular(99),
                ),
                child: Text(labels[i],
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: state.tab == i ? FontWeight.w600 : FontWeight.w400,
                      color: state.tab == i ? t.text : t.bg,
                    )),
              ),
            ),
          ),
      ]),
    );
  }
}

// ---------------------------------------------------------------- shared widgets

class _DeviceCard extends StatelessWidget {
  final AppState s;
  const _DeviceCard(this.s);
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: t.surface,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: t.line),
        boxShadow: t.sh,
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(AppState.deviceName,
                  style: TextStyle(
                      fontSize: 14, fontWeight: FontWeight.w500, color: t.text)),
              Text(AppState.category, style: TextStyle(fontSize: 12, color: t.muted)),
            ]),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
                color: t.surface2, borderRadius: BorderRadius.circular(99)),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Container(
                  width: 7,
                  height: 7,
                  decoration: BoxDecoration(
                      shape: BoxShape.circle, color: s.restricted ? t.err : t.ok)),
              const SizedBox(width: 6),
              Text(s.restricted ? 'Restricted' : 'Active',
                  style: TextStyle(fontSize: 12, color: t.text)),
            ]),
          ),
        ]),
        const SizedBox(height: 10),
        Semantics(
          label: '${s.pct} percent owned',
          child: ClipRRect(
            borderRadius: BorderRadius.circular(99),
            child: LinearProgressIndicator(
              value: s.paid / AppState.total,
              minHeight: 8,
              backgroundColor: t.surface2,
              color: t.text,
            ),
          ),
        ),
        const SizedBox(height: 6),
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          Text('${s.pct}% owned', style: TextStyle(fontSize: 12, color: t.muted)),
          Text('${fmt(s.paid)} of ${fmt(AppState.total)} TZS',
              style: TextStyle(fontSize: 12, color: t.muted)),
        ]),
      ]),
    );
  }
}

class _TxCard extends StatelessWidget {
  final List<Tx> items;
  const _TxCard(this.items);
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 2),
      decoration: BoxDecoration(
          color: t.card, borderRadius: BorderRadius.circular(26), boxShadow: t.sh),
      child: Column(children: [
        for (var i = 0; i < items.length; i++)
          Container(
            padding: const EdgeInsets.symmetric(vertical: 8),
            decoration: BoxDecoration(
                border: i == 0 ? null : Border(top: BorderSide(color: t.cline))),
            child: Row(children: [
              Container(
                width: 30,
                height: 30,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                    shape: BoxShape.circle, border: Border.all(color: t.ctext, width: 1.5)),
                child: Text('IN', style: TextStyle(fontSize: 11, color: t.ctext)),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(items[i].name,
                      style: TextStyle(
                          fontSize: 14, fontWeight: FontWeight.w500, color: t.ctext)),
                  Text('${items[i].when} · ${items[i].sub}',
                      style: TextStyle(fontSize: 12, color: t.cmuted)),
                ]),
              ),
              Text('${fmt(items[i].amount)} TZS',
                  style: TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: t.ctext,
                      fontFeatures: _tabular)),
            ]),
          ),
      ]),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  final VoidCallback onTap;
  const _Chip(this.label, this.onTap);
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(99),
      child: Container(
        height: 34,
        padding: const EdgeInsets.symmetric(horizontal: 14),
        alignment: Alignment.center,
        decoration: BoxDecoration(
          color: t.surface,
          borderRadius: BorderRadius.circular(99),
          border: Border.all(color: t.line),
          boxShadow: t.sh,
        ),
        child: Text(label,
            style: TextStyle(fontSize: 13, color: t.text, fontFeatures: _tabular)),
      ),
    );
  }
}

List<Widget> quickChips(AppState s) {
  final opts = <MapEntry<String, int>>[
    if (s.due > 0) MapEntry('Full ${fmt(s.due)}', s.due),
    if (s.due > 0) MapEntry('Half ${fmt((s.due / 2).round())}', (s.due / 2).round()),
    const MapEntry('10,000', 10000),
  ].where((e) => e.value <= s.remaining && e.value > 0).toList();
  return [
    for (final o in opts)
      Padding(
        padding: const EdgeInsets.only(right: 8),
        child: _Chip(o.key, () => s.setDraft('${o.value}')),
      ),
  ];
}

class Keypad extends StatelessWidget {
  final ValueChanged<String> onKey;
  final bool triple;
  const Keypad({super.key, required this.onKey, this.triple = true});
  @override
  Widget build(BuildContext context) {
    final rows = [
      ['1', '2', '3'],
      ['4', '5', '6'],
      ['7', '8', '9'],
      [triple ? '000' : '', '0', '⌫'],
    ];
    return Column(children: [
      for (final r in rows)
        Expanded(
          child: Row(children: [
            for (final k in r)
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.all(3),
                  child: k.isEmpty ? const SizedBox.shrink() : _Key(k, onKey),
                ),
              ),
          ]),
        ),
    ]);
  }
}

class _Key extends StatelessWidget {
  final String k;
  final ValueChanged<String> onKey;
  const _Key(this.k, this.onKey);
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return Semantics(
      button: true,
      label: k == '⌫' ? 'Delete' : k,
      excludeSemantics: true,
      child: Container(
        decoration: BoxDecoration(
            color: t.surface2, borderRadius: BorderRadius.circular(99), boxShadow: t.sh),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            borderRadius: BorderRadius.circular(99),
            onTap: () => onKey(k),
            child: Center(
              child: k == '⌫'
                  ? Icon(Icons.backspace_outlined, size: 20, color: t.text)
                  : Text(k, style: TextStyle(fontSize: 20, color: t.text)),
            ),
          ),
        ),
      ),
    );
  }
}

class _PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;
  const _PrimaryButton(this.label, this.onTap);
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    final on = onTap != null;
    return SizedBox(
      height: 48,
      child: Material(
        color: on ? Tk.red : t.surface2,
        borderRadius: BorderRadius.circular(99),
        child: InkWell(
          borderRadius: BorderRadius.circular(99),
          onTap: onTap,
          child: Center(
            child: Text(label,
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                    color: on ? Colors.white : t.muted)),
          ),
        ),
      ),
    );
  }
}

class _SecondaryButton extends StatelessWidget {
  final String label;
  final VoidCallback? onTap;
  const _SecondaryButton(this.label, this.onTap);
  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return SizedBox(
      height: 48,
      child: Material(
        color: t.surface2,
        borderRadius: BorderRadius.circular(99),
        child: InkWell(
          borderRadius: BorderRadius.circular(99),
          onTap: onTap,
          child: Center(
            child: Text(label,
                style: TextStyle(
                    fontSize: 14, color: onTap == null ? t.muted : t.text)),
          ),
        ),
      ),
    );
  }
}

// ---------------------------------------------------------------- review sheet

Future<bool> showReview(
  BuildContext context, {
  required String title,
  required String note,
  required List<List<String>> rows,
}) async {
  final r = await showModalBottomSheet<bool>(
    context: context,
    isScrollControlled: true,
    isDismissible: false,
    enableDrag: false,
    backgroundColor: tk(context).surface,
    shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
    builder: (_) => _ReviewSheet(title: title, note: note, rows: rows),
  );
  return r == true;
}

class _ReviewSheet extends StatefulWidget {
  final String title, note;
  final List<List<String>> rows;
  const _ReviewSheet({required this.title, required this.note, required this.rows});
  @override
  State<_ReviewSheet> createState() => _ReviewSheetState();
}

class _ReviewSheetState extends State<_ReviewSheet> {
  bool busy = false;

  Future<void> confirm() async {
    if (busy) return; // prevents duplicate submissions
    setState(() => busy = true);
    await Future<void>.delayed(const Duration(milliseconds: 900));
    if (!mounted) return;
    Navigator.of(context).pop(true);
  }

  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(16, 20, 16, 12),
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Align(
            alignment: Alignment.centerLeft,
            child: Text(widget.title,
                style: TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w500, color: t.text)),
          ),
          const SizedBox(height: 6),
          Align(
            alignment: Alignment.centerLeft,
            child: Text(widget.note, style: TextStyle(fontSize: 13, color: t.muted)),
          ),
          const SizedBox(height: 12),
          for (var i = 0; i < widget.rows.length; i++)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(border: Border(top: BorderSide(color: t.line))),
              child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                Text(widget.rows[i][0], style: TextStyle(fontSize: 14, color: t.muted)),
                Flexible(
                  child: Text(widget.rows[i][1],
                      textAlign: TextAlign.right,
                      style: TextStyle(
                          fontSize: 14,
                          color: t.text,
                          fontFeatures: _tabular,
                          fontWeight: i == 2 ? FontWeight.w600 : FontWeight.w400)),
                ),
              ]),
            ),
          const SizedBox(height: 14),
          Row(children: [
            Expanded(
              child: _SecondaryButton(
                  'Cancel', busy ? null : () => Navigator.of(context).pop(false)),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _PrimaryButton(
                  busy ? 'Processing demo…' : 'Confirm demo', busy ? null : confirm),
            ),
          ]),
        ]),
      ),
    );
  }
}

// ---------------------------------------------------------------- Home

class HomeTab extends StatelessWidget {
  final AppState state;
  const HomeTab({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    final s = state;
    final dueLine = 'TZS · ' +
        (s.remaining == 0
            ? 'Fully paid'
            : s.due == 0
                ? 'Paid, next due ${AppState.nextDue}'
                : 'due ${AppState.nextDue}');
    return SingleChildScrollView(
      child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Padding(
          padding: const EdgeInsets.symmetric(vertical: 10),
          child: Column(children: [
            Text('Amount due this month (demo)',
                style: TextStyle(fontSize: 13, color: t.muted)),
            const SizedBox(height: 4),
            Semantics(
              label: s.hide ? 'Amount hidden' : '${fmt(s.due)} Tanzanian shillings due',
              excludeSemantics: true,
              child: Text(s.hide ? '••••••' : fmt(s.due),
                  style: TextStyle(
                      fontSize: 42,
                      fontWeight: FontWeight.w600,
                      letterSpacing: -1,
                      color: t.text,
                      fontFeatures: _tabular)),
            ),
            Text(dueLine, style: TextStyle(fontSize: 13, color: t.muted)),
          ]),
        ),
        // Primary action
        Semantics(
          button: true,
          label: 'Pay installment',
          child: Material(
            color: Tk.red,
            borderRadius: BorderRadius.circular(99),
            elevation: 0,
            child: InkWell(
              borderRadius: BorderRadius.circular(99),
              onTap: () => s.go(1),
              child: Container(
                height: 56,
                padding: const EdgeInsets.only(left: 10, right: 18),
                child: Row(children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: const BoxDecoration(
                        shape: BoxShape.circle, color: Color(0x33FFFFFF)),
                    child: const Icon(Icons.credit_card, size: 20, color: Colors.white),
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Pay installment',
                              style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w500,
                                  color: Colors.white)),
                          Text('Toward your ${AppState.category}',
                              style: TextStyle(fontSize: 12, color: Colors.white)),
                        ]),
                  ),
                  const Icon(Icons.chevron_right, color: Colors.white),
                ]),
              ),
            ),
          ),
        ),
        const SizedBox(height: 10),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(children: [
            for (final c in quickChips(s)) c,
          ]),
        ),
        const SizedBox(height: 10),
        _DeviceCard(s),
        const SizedBox(height: 10),
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
          Text('Recent',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500, color: t.text)),
          TextButton(
            onPressed: () => s.go(3),
            child: Text('See all', style: TextStyle(color: t.text)),
          ),
        ]),
        if (s.txs.isEmpty)
          Padding(
            padding: const EdgeInsets.all(12),
            child: Text('No payments yet.', style: TextStyle(color: t.muted)),
          )
        else
          _TxCard(s.txs.take(2).toList()),
        const SizedBox(height: 8),
      ]),
    );
  }
}

// ---------------------------------------------------------------- Pay

class PayTab extends StatefulWidget {
  final AppState state;
  const PayTab({super.key, required this.state});
  @override
  State<PayTab> createState() => _PayTabState();
}

class _PayTabState extends State<PayTab> {
  String method = 'M-Pesa';
  String? error;

  AppState get s => widget.state;
  int get amount => s.draft.isEmpty ? 0 : int.parse(s.draft);

  String? validate() {
    if (s.draft.isEmpty) return 'Enter an amount.';
    if (amount < 1) return 'Amount must be more than 0.';
    if (amount > s.remaining) {
      return 'That is more than the remaining ${fmt(s.remaining)} TZS.';
    }
    return null;
  }

  Future<void> review() async {
    final e = validate();
    setState(() => error = e);
    if (e != null) return;
    final n = amount;
    final ok = await showReview(
      context,
      title: 'Review: Pay installment',
      note: 'Demo payment. No money will move and your device is not affected.',
      rows: [
        ['Appliance', AppState.deviceName],
        ['Method', method],
        ['Amount', '${fmt(n)} TZS'],
        ['Due after', '${fmt(math.max(0, s.due - n))} TZS'],
        ['Remaining after', '${fmt(s.remaining - n)} TZS'],
      ],
    );
    if (!mounted) return;
    if (ok) {
      s.pay(n, method);
      s.setDraft('');
      toast(context, 'Demo payment recorded. No money moved and your device was not changed.');
    } else {
      toast(context, 'Cancelled. No payment was recorded.');
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    final n = amount;
    final pre = n < 1
        ? ''
        : 'Due after ${fmt(math.max(0, s.due - n))} · Remaining ${fmt(math.max(0, s.remaining - n))} TZS';
    return LayoutBuilder(builder: (context, box) {
      final h = box.maxHeight;
      final keypadH = math.max(160.0, h * 0.40);
      final amountH = math.max(90.0, h - keypadH - 150);
      return SingleChildScrollView(
        child: ConstrainedBox(
          constraints: BoxConstraints(minHeight: h),
          child: Column(children: [
            SizedBox(
              height: amountH,
              child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                Text('Amount toward your ${AppState.category} (TZS)',
                    style: TextStyle(fontSize: 13, color: t.muted)),
                const SizedBox(height: 2),
                Semantics(
                  label: 'Amount ${s.draft.isEmpty ? 0 : fmt(n)} Tanzanian shillings',
                  excludeSemantics: true,
                  child: Text(s.draft.isEmpty ? '0' : fmt(n),
                      style: TextStyle(
                          fontSize: 46,
                          fontWeight: FontWeight.w600,
                          letterSpacing: -1,
                          color: s.draft.isEmpty ? t.muted : t.text,
                          fontFeatures: _tabular)),
                ),
                SizedBox(
                  height: 20,
                  child: error == null
                      ? null
                      : Text('Error: $error',
                          style: TextStyle(fontSize: 13, color: t.err)),
                ),
              ]),
            ),
            SizedBox(
              height: 34,
              child: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(children: quickChips(s)),
              ),
            ),
            const SizedBox(height: 6),
            SizedBox(
              height: keypadH,
              child: Keypad(
                onKey: (k) {
                  if (error != null) setState(() => error = null);
                  s.setDraft(applyKey(s.draft, k, 9));
                },
              ),
            ),
            SizedBox(
              height: 24,
              child: Center(
                child: Text(pre, style: TextStyle(fontSize: 13, color: t.muted)),
              ),
            ),
            Row(children: [
              Expanded(
                flex: 6,
                child: Container(
                  height: 48,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  decoration: BoxDecoration(
                    color: t.surface,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: t.field),
                  ),
                  child: DropdownButtonHideUnderline(
                    child: DropdownButton<String>(
                      value: method,
                      isExpanded: true,
                      dropdownColor: t.surface,
                      style: TextStyle(fontSize: 14, color: t.text),
                      items: [
                        for (final m in const ['M-Pesa', 'Bank transfer', 'Card'])
                          DropdownMenuItem(value: m, child: Text('Pay with $m')),
                      ],
                      onChanged: (v) => setState(() => method = v ?? method),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(flex: 5, child: _PrimaryButton('Review', review)),
            ]),
            const SizedBox(height: 8),
          ]),
        ),
      );
    });
  }
}

// ---------------------------------------------------------------- Device

class DeviceTab extends StatelessWidget {
  final AppState state;
  const DeviceTab({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    final s = state;
    final cells = [
      ['Total price', '${fmt(AppState.total)} TZS'],
      ['Paid so far', '${fmt(s.paid)} TZS'],
      ['Remaining', '${fmt(s.remaining)} TZS'],
      ['Monthly installment', '${fmt(AppState.monthly)} TZS'],
      ['Next due', AppState.nextDue],
      ['Payments left', '${s.left}'],
    ];
    final status = (s.restricted
            ? 'Your device is Restricted until the amount due is paid.'
            : 'Your device is Active and works normally.') +
        (s.tvLinked ? ' TV linked (demo).' : ' TV not linked yet.');
    return SingleChildScrollView(
      child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
        Text('My device',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w500, color: t.text)),
        const SizedBox(height: 8),
        _DeviceCard(s),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
              color: t.surface, borderRadius: BorderRadius.circular(20), boxShadow: t.sh),
          child: Column(children: [
            for (var r = 0; r < 3; r++)
              Container(
                decoration: BoxDecoration(
                    border: r == 0 ? null : Border(top: BorderSide(color: t.line))),
                padding: const EdgeInsets.symmetric(vertical: 8),
                child: Row(children: [
                  for (var c = 0; c < 2; c++)
                    Expanded(
                      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Text(cells[r * 2 + c][0],
                            style: TextStyle(fontSize: 13, color: t.muted)),
                        Text(cells[r * 2 + c][1],
                            style: TextStyle(
                                fontSize: 13,
                                fontWeight: FontWeight.w500,
                                color: t.text,
                                fontFeatures: _tabular)),
                      ]),
                    ),
                ]),
              ),
          ]),
        ),
        const SizedBox(height: 8),
        Text(status, style: TextStyle(fontSize: 13, color: t.muted)),
        const SizedBox(height: 8),
        Row(children: [
          Expanded(
            child: _PrimaryButton('Link TV', () {
              Navigator.of(context).push(
                  MaterialPageRoute(builder: (_) => LinkTvPage(state: s)));
            }),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: _SecondaryButton(
              s.restricted ? 'Demo: simulate paid up' : 'Demo: simulate overdue',
              (s.due == 0 && !s.restricted) ? null : s.toggleRestricted,
            ),
          ),
        ]),
        const SizedBox(height: 6),
        Text('Demo only: ORCA Cloud decides the real status.',
            style: TextStyle(fontSize: 13, color: t.muted)),
      ]),
    );
  }
}

// ---------------------------------------------------------------- History

class HistoryTab extends StatelessWidget {
  final AppState state;
  const HistoryTab({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    final s = state;
    return Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      Text('Payment history',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w500, color: t.text)),
      const SizedBox(height: 8),
      Expanded(
        child: s.txs.isEmpty
            ? Align(
                alignment: Alignment.topLeft,
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Text(
                      'No payments yet. Pay an installment and it will appear here.',
                      style: TextStyle(fontSize: 14, color: t.muted)),
                ),
              )
            : SingleChildScrollView(child: _TxCard(s.txs)),
      ),
      const SizedBox(height: 8),
      _SecondaryButton('Reset demo', s.reset),
    ]);
  }
}

// ---------------------------------------------------------------- Link TV

class LinkTvPage extends StatefulWidget {
  final AppState state;
  const LinkTvPage({super.key, required this.state});
  @override
  State<LinkTvPage> createState() => _LinkTvPageState();
}

class _LinkTvPageState extends State<LinkTvPage> {
  String code = '';
  String? error;

  String get shown => code.length > 3 ? '${code.substring(0, 3)} ${code.substring(3)}' : code;

  String? validate() {
    if (code.isEmpty) return 'Enter the 6-digit code shown on your TV.';
    if (code.length < 6) return 'The code has 6 digits. You entered ${code.length}.';
    return null;
  }

  Future<void> submit() async {
    final e = validate();
    setState(() => error = e);
    if (e != null) return;
    final shownCode = shown;
    final ok = await showReview(
      context,
      title: 'Review: Link TV',
      note: 'Demo link. No real TV will be connected.',
      rows: [
        ['Activation code', shownCode],
        ['Appliance', AppState.deviceName],
      ],
    );
    if (!mounted) return;
    if (ok) {
      widget.state.linkTv();
      final nav = Navigator.of(context);
      final messenger = ScaffoldMessenger.of(context);
      nav.pop();
      messenger.showSnackBar(const SnackBar(
        content: Text('Demo: TV linked. No real TV was connected.'),
        behavior: SnackBarBehavior.floating,
      ));
    } else {
      toast(context, 'Cancelled. Your TV was not linked.');
    }
  }

  @override
  Widget build(BuildContext context) {
    final t = tk(context);
    return Scaffold(
      backgroundColor: t.bg,
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 480),
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 8, 16, 12),
              child: LayoutBuilder(builder: (context, box) {
                final h = box.maxHeight;
                final keypadH = math.max(160.0, h * 0.42);
                final codeH = math.max(90.0, h - keypadH - 150);
                return SingleChildScrollView(
                  child: ConstrainedBox(
                    constraints: BoxConstraints(minHeight: h),
                    child: Column(children: [
                      Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
                        TextButton(
                          onPressed: () => Navigator.of(context).pop(),
                          child: Text('← Back', style: TextStyle(color: t.text)),
                        ),
                        Text('Link TV',
                            style: TextStyle(
                                fontSize: 20, fontWeight: FontWeight.w500, color: t.text)),
                      ]),
                      SizedBox(
                        height: codeH,
                        child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
                          Text('Activation code shown on your TV',
                              style: TextStyle(fontSize: 13, color: t.muted)),
                          const SizedBox(height: 2),
                          Text(code.isEmpty ? '000 000' : shown,
                              style: TextStyle(
                                  fontSize: 44,
                                  fontWeight: FontWeight.w600,
                                  letterSpacing: 4,
                                  color: code.isEmpty ? t.muted : t.text,
                                  fontFeatures: _tabular)),
                          SizedBox(
                            height: 20,
                            child: error == null
                                ? null
                                : Text('Error: $error',
                                    style: TextStyle(fontSize: 13, color: t.err)),
                          ),
                        ]),
                      ),
                      SizedBox(
                        height: keypadH,
                        child: Keypad(
                          triple: false,
                          onKey: (k) => setState(() {
                            error = null;
                            code = applyKey(code, k, 6);
                          }),
                        ),
                      ),
                      SizedBox(
                        height: 24,
                        child: Center(
                          child: Text(code.length == 6 ? 'Demo: any 6-digit code works.' : '',
                              style: TextStyle(fontSize: 13, color: t.muted)),
                        ),
                      ),
                      SizedBox(
                          width: double.infinity, child: _PrimaryButton('Link TV', submit)),
                    ]),
                  ),
                );
              }),
            ),
          ),
        ),
      ),
    );
  }
}
