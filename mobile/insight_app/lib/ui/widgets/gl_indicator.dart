import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../config/constants.dart';

/// Animated GL indicator — circular progress ring with count-up number.
class GlIndicator extends StatefulWidget {
  final double glycemicLoad;
  final String glLevel;

  const GlIndicator({
    super.key,
    required this.glycemicLoad,
    required this.glLevel,
  });

  @override
  State<GlIndicator> createState() => _GlIndicatorState();
}

class _GlIndicatorState extends State<GlIndicator>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _progressAnimation;
  late Animation<double> _countAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: AppDurations.countUp,
    );

    final maxGL = 40.0; // GL scale max for visual
    final progress = (widget.glycemicLoad / maxGL).clamp(0.0, 1.0);

    _progressAnimation = Tween<double>(begin: 0, end: progress).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );
    _countAnimation =
        Tween<double>(begin: 0, end: widget.glycemicLoad).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Color get _color => switch (widget.glLevel.toLowerCase()) {
        'low' => AppColors.glLow,
        'medium' => AppColors.glMedium,
        'high' => AppColors.glHigh,
        _ => AppColors.textMuted,
      };

  String get _label => switch (widget.glLevel.toLowerCase()) {
        'low' => 'Thấp',
        'medium' => 'Trung bình',
        'high' => 'Cao',
        _ => widget.glLevel,
      };

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, _) {
        return SizedBox(
          width: 200,
          height: 200,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Background ring
              SizedBox(
                width: 200,
                height: 200,
                child: CircularProgressIndicator(
                  value: 1.0,
                  strokeWidth: 10,
                  color: _color.withAlpha(30),
                  strokeCap: StrokeCap.round,
                ),
              ),
              // Animated progress ring
              SizedBox(
                width: 200,
                height: 200,
                child: CircularProgressIndicator(
                  value: _progressAnimation.value,
                  strokeWidth: 10,
                  color: _color,
                  strokeCap: StrokeCap.round,
                ),
              ),
              // Center content
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    'GL',
                    style: GoogleFonts.inter(
                      fontSize: 14,
                      color: AppColors.textMuted,
                    ),
                  ),
                  Text(
                    _countAnimation.value.toStringAsFixed(1),
                    style: GoogleFonts.inter(
                      fontSize: 46,
                      fontWeight: FontWeight.bold,
                      color: _color,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 14, vertical: 4),
                    decoration: BoxDecoration(
                      color: _color,
                      borderRadius: BorderRadius.circular(AppRadius.pill),
                    ),
                    child: Text(
                      _label,
                      style: GoogleFonts.inter(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 13,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        );
      },
    );
  }
}
