function txt = jsonencode(varargin)
%JSONENCODE  Stand-in for releases whose jsonencode lacks 'PrettyPrint' (R2021a+).
%   Removes the 'PrettyPrint' name-value pair and calls the built-in encoder,
%   so lesson code runs unchanged. The output is compact JSON, not indented.
%
%   Added by setup_path only when the built-in rejects 'PrettyPrint'. It
%   shadows the built-in on purpose while this folder is on the path.

args = varargin;
k = 2;
while k <= numel(args) - 1
    name = args{k};
    if (ischar(name) || isstring(name)) && strcmpi(char(name), 'PrettyPrint')
        args(k:k+1) = [];
    else
        k = k + 2;
    end
end
txt = builtin('jsonencode', args{:});
end
