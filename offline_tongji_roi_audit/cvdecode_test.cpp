#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
#include <fstream>

int main(int argc, char** argv) {
  if (argc < 2) return 2;
  std::ifstream in(argv[1], std::ios::binary);
  std::vector<unsigned char> bytes((std::istreambuf_iterator<char>(in)), {});
  cv::Mat decoded = cv::imdecode(bytes, cv::IMREAD_COLOR);
  cv::Mat direct = cv::imread(argv[1], cv::IMREAD_COLOR);
  std::cout << bytes.size() << " memory=" << decoded.cols << "x" << decoded.rows << " direct=" << direct.cols << "x" << direct.rows << " channels=" << decoded.channels() << std::endl;
  return decoded.empty() ? 1 : 0;
}
