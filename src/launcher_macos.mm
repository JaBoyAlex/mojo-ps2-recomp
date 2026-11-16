// Cocoa frontend for the same headless bootstrap used by RecompLauncher.
#import <Cocoa/Cocoa.h>
#include <unistd.h>
#include <cstdio>
#include <string>
#include <vector>

int main(int argc, char **argv) {
    @autoreleasepool {
        if (argc == 2 && std::string(argv[1]) == "--self-test") {
            puts("MOJO native macOS launcher"); return 0;
        }
        NSString *root = [[NSBundle mainBundle] resourcePath];
        NSMutableArray<NSString *> *arguments = [NSMutableArray arrayWithObjects:
            [root stringByAppendingPathComponent:@"builder/bootstrap.sh"], root, nil];
        bool prepare = false, game = false;
        for (int i=1; i<argc; ++i) {
            NSString *arg = [NSString stringWithUTF8String:argv[i]];
            // Finder can supply a process serial number; it is not a builder option.
            if ([arg hasPrefix:@"-psn_"]) continue;
            [arguments addObject:arg];
            prepare |= [arg isEqualToString:@"--prepare"];
            game |= [arg isEqualToString:@"--game"];
        }
        if (prepare) {
            std::vector<std::string> strings = {"sh"};
            for (NSString *arg in arguments) strings.emplace_back([arg UTF8String]);
            std::vector<char *> pointers;
            for (auto &arg : strings) pointers.push_back(arg.data());
            pointers.push_back(nullptr);
            execv("/bin/sh", pointers.data()); return 21;
        }
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        [NSApp activateIgnoringOtherApps:YES];
        NSString *disc = [NSHomeDirectory() stringByAppendingPathComponent:@"Library/Application Support/MOJO Recomp/disc.iso"];
        if (!game && ![[NSFileManager defaultManager] fileExistsAtPath:disc]) {
            NSOpenPanel *picker = [NSOpenPanel openPanel];
            picker.title = @"Select your MOJO! USA PS2 ISO, CHD or CUE/BIN";
            picker.canChooseDirectories = NO;
            if ([picker runModal] != NSModalResponseOK) return 20;
            [arguments addObjectsFromArray:@[@"--game", picker.URL.path]];
        }
        NSWindow *window = [[NSWindow alloc] initWithContentRect:NSMakeRect(0,0,600,120)
            styleMask:NSWindowStyleMaskTitled backing:NSBackingStoreBuffered defer:NO];
        window.title = @"MOJO! — preparing your local game";
        NSTextField *status = [NSTextField labelWithString:@"Preparing verified tools. First setup can take several minutes."];
        status.frame = NSMakeRect(20,55,560,45);
        NSProgressIndicator *progress = [[NSProgressIndicator alloc] initWithFrame:NSMakeRect(20,25,560,20)];
        progress.indeterminate = NO; progress.minValue = 0; progress.maxValue = 1;
        [window.contentView addSubview:status]; [window.contentView addSubview:progress];
        [window center]; [window makeKeyAndOrderFront:nil];
        NSTask *task = [[NSTask alloc] init];
        task.executableURL = [NSURL fileURLWithPath:@"/bin/sh"];
        task.arguments = arguments;
        NSPipe *pipe = [NSPipe pipe]; task.standardOutput = pipe; task.standardError = pipe;
        __block NSString *pending = @"";
        __block NSString *last = @"Setup failed. Check native prerequisites and your private local logs.";
        pipe.fileHandleForReading.readabilityHandler = ^(NSFileHandle *handle) {
            NSData *data = [handle availableData];
            if (!data.length) { handle.readabilityHandler = nil; return; }
            NSString *text = [[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding];
            if (!text) return;
            dispatch_async(dispatch_get_main_queue(), ^{
                pending = [pending stringByAppendingString:text];
                NSRange newline;
                while ((newline = [pending rangeOfString:@"\n"]).location != NSNotFound) {
                    NSString *line = [pending substringToIndex:newline.location];
                    pending = [pending substringFromIndex:newline.location+1];
                    if (line.length) last = line;
                    if ([line hasPrefix:@"progress "]) {
                        NSArray *parts = [line componentsSeparatedByString:@" "];
                        if (parts.count >= 3) {
                            progress.doubleValue = [parts[1] doubleValue];
                            status.stringValue = [[parts subarrayWithRange:NSMakeRange(2,parts.count-2)] componentsJoinedByString:@" "];
                            if (progress.doubleValue >= 1) [window orderOut:nil];
                        }
                    }
                }
            });
        };
        __block int result = 21;
        task.terminationHandler = ^(NSTask *finished) {
            dispatch_async(dispatch_get_main_queue(), ^{
                result = finished.terminationStatus;
                if (result) {
                    NSAlert *alert = [[NSAlert alloc] init]; alert.messageText = @"MOJO! could not start";
                    alert.informativeText = last; [alert runModal];
                }
                [NSApp stop:nil];
                [NSApp postEvent:[NSEvent otherEventWithType:NSEventTypeApplicationDefined location:NSZeroPoint
                    modifierFlags:0 timestamp:0 windowNumber:0 context:nil subtype:0 data1:0 data2:0] atStart:NO];
            });
        };
        NSError *error = nil;
        if (![task launchAndReturnError:&error]) { fprintf(stderr,"Cannot start bootstrap\n"); return 21; }
        [NSApp run];
        return result;
    }
}
