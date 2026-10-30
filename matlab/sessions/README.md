# sessions — 내가 수정·작성한 세션 코드

`../kit/practice/<세션>`은 원본으로 두고, 변수를 바꾸거나 직접 구현할 때 여기에 세션 폴더를 만듭니다.
폴더 이름은 Notion 세션 ID와 같게 둡니다 (`W01-S1`, `W03-S3` …).

```matlab
repo = fileparts(fileparts(which('setup_path')));   % ../README.md 의 addpath 후
copyfile(fullfile(repo, 'matlab', 'kit', 'practice', 'W01-S1'), ...
         fullfile(repo, 'matlab', 'sessions', 'W01-S1'));
cd(fullfile(repo, 'matlab', 'sessions', 'W01-S1'));
which run_checks -all      % 첫 경로가 sessions/W01-S1 인지 확인
```

- git에 올리는 것: 내가 바꾸거나 새로 쓴 `.m` 파일.
- git에서 제외: `results*/`, `comparisons/`, `*.mat` 등 실행 결과 (`.gitignore`).
- 공개 저장소이므로 키트 원본을 그대로 올리지 말고, 바꾼 부분이 있는 파일만 커밋합니다 (`git add` 시 파일 지정).
- W04 이후는 키트에 미니 실습만 있습니다. 세션 코드를 직접 작성할 때도 같은 이름 규칙을 씁니다.
