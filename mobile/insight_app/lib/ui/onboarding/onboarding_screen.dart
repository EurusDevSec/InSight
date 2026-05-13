import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';

import '../../config/constants.dart';
import '../../viewmodels/settings_viewmodel.dart';

/// Onboarding — 3 slides shown on first launch.
class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final _controller = PageController();
  int _currentPage = 0;

  static const _slides = [
    _SlideData(
      icon: Icons.camera_alt_rounded,
      iconColor: AppColors.primary,
      title: 'Chụp ảnh, biết GL',
      subtitle:
          'Chỉ cần chụp ảnh món ăn\nAI sẽ ước lượng Glycemic Load trong vài giây',
    ),
    _SlideData(
      icon: Icons.medical_services_rounded,
      iconColor: AppColors.info,
      title: 'Tư vấn Insulin thông minh',
      subtitle:
          'RAG Agent phân tích 26 tài liệu y khoa\nđưa ra khuyến nghị cá nhân hóa',
    ),
    _SlideData(
      icon: Icons.verified_user_rounded,
      iconColor: AppColors.success,
      title: 'An toàn & Minh bạch',
      subtitle:
          'Giới hạn insulin 30U cứng\nBáo cáo uncertainty range\nKhông thay thế bác sĩ',
    ),
  ];

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onNext() {
    if (_currentPage < _slides.length - 1) {
      _controller.nextPage(
        duration: AppDurations.normal,
        curve: Curves.easeInOut,
      );
    } else {
      _finish();
    }
  }

  void _finish() {
    context.read<SettingsViewModel>().completeOnboarding();
    context.go('/');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Skip button
            Align(
              alignment: Alignment.topRight,
              child: TextButton(
                onPressed: _finish,
                child: Text(
                  'Bỏ qua',
                  style: TextStyle(color: AppColors.textMuted),
                ),
              ),
            ),
            // Pages
            Expanded(
              child: PageView.builder(
                controller: _controller,
                itemCount: _slides.length,
                onPageChanged: (i) => setState(() => _currentPage = i),
                itemBuilder: (context, i) => _buildSlide(_slides[i]),
              ),
            ),
            // Indicator
            Padding(
              padding: const EdgeInsets.only(bottom: AppSpacing.lg),
              child: SmoothPageIndicator(
                controller: _controller,
                count: _slides.length,
                effect: WormEffect(
                  dotColor: AppColors.textMuted.withAlpha(60),
                  activeDotColor: AppColors.primary,
                  dotHeight: 8,
                  dotWidth: 8,
                ),
              ),
            ),
            // CTA button
            Padding(
              padding: const EdgeInsets.fromLTRB(
                AppSpacing.lg,
                0,
                AppSpacing.lg,
                AppSpacing.xl,
              ),
              child: SizedBox(
                width: double.infinity,
                height: 56,
                child: FilledButton(
                  onPressed: _onNext,
                  child: Text(
                    _currentPage < _slides.length - 1
                        ? 'Tiếp tục'
                        : 'Bắt đầu',
                    style: const TextStyle(fontSize: 18),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSlide(_SlideData data) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppSpacing.xl),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 120,
            height: 120,
            decoration: BoxDecoration(
              color: data.iconColor.withAlpha(25),
              shape: BoxShape.circle,
            ),
            child: Icon(data.icon, size: 56, color: data.iconColor),
          ),
          const SizedBox(height: AppSpacing.xl),
          Text(
            data.title,
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: AppSpacing.md),
          Text(
            data.subtitle,
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(
              fontSize: 16,
              color: AppColors.textMuted,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }
}

class _SlideData {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;

  const _SlideData({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
  });
}
