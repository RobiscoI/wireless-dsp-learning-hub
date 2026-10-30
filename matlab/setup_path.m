function setup_path()
%SETUP_PATH  Prepare the MATLAB track for the MATLAB release in use.
%   Run once per MATLAB session (or call it from startup.m):
%       addpath('<repo>/matlab'); setup_path
%
%   The lessons are written for R2025b. On an older release this adds small
%   stand-ins from compat/ for the functions the lessons call but the release
%   lacks. Each stand-in folder is added only when the real function is
%   missing, so nothing is shadowed on a release that already has it.
%
%   Not covered (edit the session copy instead, see README.md):
%     sum(x, 'all')  - R2018b+, used by kit/matlab/ofdm_link_demo.m
%     uifigure GUI export (W02-S3)

here = fileparts(mfilename('fullpath'));
compat = fullfile(here, 'compat');
added = {};

% Functions that do not exist at all on old releases.
if missing('exportgraphics', compat)                                    % R2020a
    addpath(fullfile(compat, 'exportgraphics'));
    added{end+1} = 'exportgraphics';
end
if missing('tiledlayout', compat) || missing('nexttile', compat)        % R2019b
    addpath(fullfile(compat, 'tiledlayout'));
    added{end+1} = 'tiledlayout/nexttile';
end
if missing('yline', compat)                                             % R2018b
    addpath(fullfile(compat, 'yline'));
    added{end+1} = 'yline';
end

% jsonencode exists (R2016b) but 'PrettyPrint' arrived in R2021a. The
% stand-in shadows the built-in on purpose, so it is added only when needed.
if ~supports_pretty_print(compat)
    state = warning('off', 'MATLAB:dispatcher:nameConflict');
    addpath(fullfile(compat, 'jsonencode_prettyprint'));
    warning(state);
    added{end+1} = 'jsonencode(PrettyPrint)';
end

if isempty(added)
    fprintf('setup_path: MATLAB %s needs no compatibility stand-ins.\n', version('-release'));
else
    fprintf('setup_path: MATLAB %s, using stand-ins: %s\n', version('-release'), strjoin(added, ', '));
end
end

function tf = missing(name, compat)
% True when NAME does not resolve, or resolves to our own stand-in (re-run).
w = which(name);
tf = isempty(w) || strncmpi(w, compat, numel(compat));
end

function tf = supports_pretty_print(compat)
% Our stand-in already resolving means an earlier call found the option missing.
w = which('jsonencode');
if strncmpi(w, compat, numel(compat))
    tf = false;
    return;
end
try
    jsonencode(1, 'PrettyPrint', true);
    tf = true;
catch
    tf = false;
end
end
