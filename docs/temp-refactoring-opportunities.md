# Refactoring Opportunities Report

**Date**: Created after Stage 2 frontend implementation review  
**Branch**: `frontend-stage2-work`  
**Scope**: Frontend TypeScript/React code changes since diverging from `main`

---

## Summary

This report identifies refactoring opportunities in the Stage 2 frontend implementation. All issues are **non-breaking** and can be addressed incrementally to improve code maintainability, consistency, and reusability.

---

## 1. Error Handling Inconsistency

### Issue
Mixed usage of error notification functions:
- `showErrorMessage` from `@jupyterlab/apputils` (used in `WWCCoPilot.tsx`, `SynthesisWorkbench.tsx`, `index.tsx`)
- `showError` from `./utils/notifications` (used in `LibraryTab.tsx`, `DiscoveryTab.tsx`, `index.tsx`)

### Impact
- Inconsistent user experience (different dialog styles)
- Harder to maintain (two different error handling patterns)
- Code duplication

### Recommendation
**Standardize on `showError` from `./utils/notifications`** for consistency with existing codebase patterns.

**Files to Update**:
- `src/widgets/WWCCoPilot.tsx` (line 7, 44-47)
- `src/widgets/SynthesisWorkbench.tsx` (line 11, 38-41, 54-57)
- `src/index.tsx` (line 16, 205-208, 228)

**Refactoring**:
```typescript
// Change from:
import { showErrorMessage } from '@jupyterlab/apputils';
showErrorMessage('Title', 'Message');

// To:
import { showError } from '../utils/notifications';
showError('Title', 'Message');
```

**Priority**: Medium - Improves consistency

---

## 2. Custom Event Communication Pattern

### Issue
Custom events are dispatched and listened to directly using `window.dispatchEvent` and `window.addEventListener` without abstraction.

**Current Pattern** (repeated in 3 places):
- `LibraryTab.tsx`: Dispatches `open-synthesis-workbench`
- `DetailView.tsx`: Dispatches `open-wwc-copilot`
- `index.tsx`: Listens to both events

### Impact
- No type safety for event data
- Hard to discover what events exist
- Easy to introduce typos in event names
- No centralized documentation

### Recommendation
**Create a custom event utility module** (`src/utils/events.ts`):

```typescript
// src/utils/events.ts
export namespace AppEvents {
  export const OPEN_SYNTHESIS_WORKBENCH = 'open-synthesis-workbench';
  export const OPEN_WWC_COPILOT = 'open-wwc-copilot';
  
  export interface OpenSynthesisWorkbenchDetail {
    paperIds: number[];
  }
  
  export interface OpenWWCCopilotDetail {
    paperId: number;
    paperTitle: string;
  }
  
  export function dispatchOpenSynthesisWorkbench(paperIds: number[]): void {
    window.dispatchEvent(
      new CustomEvent<OpenSynthesisWorkbenchDetail>(
        OPEN_SYNTHESIS_WORKBENCH,
        { detail: { paperIds } }
      )
    );
  }
  
  export function dispatchOpenWWCCopilot(paperId: number, paperTitle: string): void {
    window.dispatchEvent(
      new CustomEvent<OpenWWCCopilotDetail>(
        OPEN_WWC_COPILOT,
        { detail: { paperId, paperTitle } }
      )
    );
  }
  
  export function onOpenSynthesisWorkbench(
    handler: (detail: OpenSynthesisWorkbenchDetail) => void
  ): () => void {
    const listener = ((event: CustomEvent<OpenSynthesisWorkbenchDetail>) => {
      handler(event.detail);
    }) as EventListener;
    
    window.addEventListener(OPEN_SYNTHESIS_WORKBENCH, listener);
    return () => window.removeEventListener(OPEN_SYNTHESIS_WORKBENCH, listener);
  }
  
  export function onOpenWWCCopilot(
    handler: (detail: OpenWWCCopilotDetail) => void
  ): () => void {
    const listener = ((event: CustomEvent<OpenWWCCopilotDetail>) => {
      handler(event.detail);
    }) as EventListener;
    
    window.addEventListener(OPEN_WWC_COPILOT, listener);
    return () => window.removeEventListener(OPEN_WWC_COPILOT, listener);
  }
}
```

**Files to Update**:
- `src/widgets/LibraryTab.tsx` (line 128-132)
- `src/widgets/DetailView.tsx` (line 148-155)
- `src/index.tsx` (line 258-283)

**Priority**: Medium - Improves type safety and maintainability

---

## 3. Loading State Pattern Duplication

### Issue
Multiple components implement the same loading state pattern:

```typescript
const [isLoading, setIsLoading] = useState(false);

const handleAction = async () => {
  setIsLoading(true);
  try {
    // ... async operation
  } catch (err) {
    // ... error handling
  } finally {
    setIsLoading(false);
  }
};
```

**Affected Files**:
- `src/widgets/WWCCoPilot.tsx` (lines 21, 35, 49)
- `src/widgets/SynthesisWorkbench.tsx` (lines 29, 32, 43, 48, 59)
- `src/widgets/LibraryTab.tsx` (lines 20, 32, 40, 101, 109)
- `src/widgets/DiscoveryTab.tsx` (lines 14, 22, 35)

### Recommendation
**Create a custom hook** `useAsyncOperation`:

```typescript
// src/utils/hooks.ts
import { useState, useCallback } from 'react';

export function useAsyncOperation<T, Args extends any[]>(
  operation: (...args: Args) => Promise<T>
): [boolean, (...args: Args) => Promise<T | undefined>, Error | null] {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  
  const execute = useCallback(async (...args: Args): Promise<T | undefined> => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await operation(...args);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error');
      setError(error);
      return undefined;
    } finally {
      setIsLoading(false);
    }
  }, [operation]);
  
  return [isLoading, execute, error];
}
```

**Usage Example**:
```typescript
// Before:
const [isLoading, setIsLoading] = useState(false);
const handleRunMetaAnalysis = async () => {
  setIsLoading(true);
  try {
    const result = await performMetaAnalysis(paperIds);
    setMetaAnalysisResult(result);
  } catch (err) {
    showErrorMessage('Error', err.message);
  } finally {
    setIsLoading(false);
  }
};

// After:
const [isLoading, runMetaAnalysis, error] = useAsyncOperation(performMetaAnalysis);
const handleRunMetaAnalysis = async () => {
  const result = await runMetaAnalysis(paperIds);
  if (result) {
    setMetaAnalysisResult(result);
  } else if (error) {
    showError('Error', error.message);
  }
};
```

**Priority**: High - Reduces code duplication significantly

---

## 4. Boolean Select Input Pattern

### Issue
`WWCCoPilot.tsx` has repeated pattern for boolean select inputs (lines 113-132, 135-156):

```typescript
<select
  value={
    judgments.randomization_documented === undefined
      ? ''
      : String(judgments.randomization_documented)
  }
  onChange={e =>
    setJudgments({
      ...judgments,
      randomization_documented:
        e.target.value === ''
          ? undefined
          : e.target.value === 'true'
    })
  }
>
  <option value="">Not specified</option>
  <option value="true">Yes</option>
  <option value="false">No</option>
</select>
```

### Recommendation
**Create a reusable `BooleanSelect` component**:

```typescript
// src/widgets/BooleanSelect.tsx
import React from 'react';

interface IBooleanSelectProps {
  value: boolean | undefined;
  onChange: (value: boolean | undefined) => void;
  label: string;
  nullOptionLabel?: string;
  trueLabel?: string;
  falseLabel?: string;
  helpText?: string;
}

export const BooleanSelect: React.FC<IBooleanSelectProps> = ({
  value,
  onChange,
  label,
  nullOptionLabel = 'Not specified',
  trueLabel = 'Yes',
  falseLabel = 'No',
  helpText
}) => {
  return (
    <div className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-field">
      <label>{label}</label>
      <select
        value={value === undefined ? '' : String(value)}
        onChange={e =>
          onChange(
            e.target.value === ''
              ? undefined
              : e.target.value === 'true'
          )
        }
      >
        <option value="">{nullOptionLabel}</option>
        <option value="true">{trueLabel}</option>
        <option value="false">{falseLabel}</option>
      </select>
      {helpText && (
        <p className="jp-jupyterlab-research-assistant-wwc-copilot-wwc-help">
          {helpText}
        </p>
      )}
    </div>
  );
};
```

**Files to Update**:
- `src/widgets/WWCCoPilot.tsx` (replace 2 select blocks)

**Priority**: Low - Small duplication, but improves readability

---

## 5. Close Button Component

### Issue
Close button pattern repeated in multiple components:
- `WWCCoPilot.tsx` (line 67-73)
- `SynthesisWorkbench.tsx` (line 68-73)
- `DetailView.tsx` (line 24-29)

All use similar structure with `×` character and close handler.

### Recommendation
**Create a reusable `CloseButton` component**:

```typescript
// src/widgets/CloseButton.tsx
import React from 'react';

interface ICloseButtonProps {
  onClick: () => void;
  className?: string;
  ariaLabel?: string;
}

export const CloseButton: React.FC<ICloseButtonProps> = ({
  onClick,
  className = 'jp-jupyterlab-research-assistant-wwc-copilot-close',
  ariaLabel = 'Close'
}) => {
  return (
    <button
      onClick={onClick}
      className={className}
      aria-label={ariaLabel}
    >
      ×
    </button>
  );
};
```

**Priority**: Low - Small duplication, but improves consistency

---

## 6. Tab Component Abstraction

### Issue
Tab navigation pattern used in:
- `SynthesisWorkbench.tsx` (lines 100-121)
- `DetailView.tsx` (lines 43-66)

Both implement similar tab switching logic.

### Recommendation
**Create a reusable `Tabs` component**:

```typescript
// src/widgets/Tabs.tsx
import React from 'react';

interface ITab {
  id: string;
  label: string;
  badge?: number | string;
}

interface ITabsProps {
  tabs: ITab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  className?: string;
}

export const Tabs: React.FC<ITabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
  className = 'jp-jupyterlab-research-assistant-wwc-copilot-tabs'
}) => {
  return (
    <div className={className}>
      {tabs.map(tab => (
        <button
          key={tab.id}
          className={
            activeTab === tab.id
              ? 'jp-jupyterlab-research-assistant-wwc-copilot-tab-active'
              : 'jp-jupyterlab-research-assistant-wwc-copilot-tab'
          }
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
          {tab.badge !== undefined && ` (${tab.badge})`}
        </button>
      ))}
    </div>
  );
};
```

**Priority**: Medium - Reduces duplication and improves consistency

---

## 7. Empty State Component

### Issue
Empty state messages appear in multiple components:
- `LibraryTab.tsx` (line 219-223)
- `SynthesisWorkbench.tsx` (line 130-133)
- `ConflictView.tsx` (line 20-23)

### Recommendation
**Create a reusable `EmptyState` component**:

```typescript
// src/widgets/EmptyState.tsx
import React from 'react';

interface IEmptyStateProps {
  message: string;
  icon?: string;
  className?: string;
}

export const EmptyState: React.FC<IEmptyStateProps> = ({
  message,
  icon,
  className = 'jp-jupyterlab-research-assistant-wwc-copilot-empty'
}) => {
  return (
    <div className={className}>
      {icon && <span className="empty-icon">{icon}</span>}
      <p>{message}</p>
    </div>
  );
};
```

**Priority**: Low - Small duplication, but improves consistency

---

## 8. File Download Utility

### Issue
File download pattern in `exportLibrary()` (lines 150-159) will be duplicated for future export functions (meta-analysis CSV, synthesis Markdown).

### Recommendation
**Extract file download logic into utility function**:

```typescript
// src/utils/file-download.ts
export function downloadFile(
  blob: Blob,
  filename: string
): void {
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}

export async function downloadFromResponse(
  response: Response,
  filename: string
): Promise<void> {
  if (!response.ok) {
    throw new Error(`Download failed: ${response.statusText}`);
  }
  const blob = await response.blob();
  downloadFile(blob, filename);
}
```

**Files to Update**:
- `src/api.ts` (refactor `exportLibrary` to use utility)

**Priority**: Medium - Prevents future duplication

---

## 9. API Error Handling Pattern

### Issue
All new API functions (`runWWCAssessment`, `performMetaAnalysis`, `detectConflicts`) have identical error handling:

```typescript
if (response.status === 'error') {
  throw new Error(response.message || 'Operation failed');
}
if (!response.data) {
  throw new Error('No data returned');
}
return response.data;
```

### Recommendation
**The existing `handleAPIResponse` utility already handles this pattern**, but the new functions don't use it consistently.

**Files to Update**:
- `src/api.ts` (lines 188-208, 236-260, 278-302)

**Refactoring**:
```typescript
// Before:
export async function runWWCAssessment(
  request: IWWCAssessmentRequest
): Promise<IWWCAssessment> {
  const response = await requestAPI<IAPIResponse<IWWCAssessment>>(
    'wwc-assessment',
    {
      method: 'POST',
      body: JSON.stringify(request)
    }
  );

  if (response.status === 'error') {
    throw new Error(response.message || 'WWC assessment failed');
  }

  if (!response.data) {
    throw new Error('No assessment data returned');
  }

  return response.data;
}

// After:
export async function runWWCAssessment(
  request: IWWCAssessmentRequest
): Promise<IWWCAssessment> {
  const response = await requestAPI<IAPIResponse<IWWCAssessment>>(
    'wwc-assessment',
    {
      method: 'POST',
      body: JSON.stringify(request)
    }
  );

  return handleAPIResponse(response, 'WWC assessment failed');
}
```

**Priority**: High - Reduces code duplication and uses existing utility

---

## 10. Interface Naming Inconsistency

### Issue
Mixed interface naming conventions:
- Some use `I` prefix: `IWWCCoPilotProps`, `IWWCAssessment`, `IWWCAssessmentRequest`, `IMetaAnalysisViewProps`, `IConflictViewProps`, `ISynthesisWorkbenchProps`, `IPaperCardProps`, `IDetailViewProps`
- Some don't: (none found, but pattern is inconsistent with React community)

### Recommendation
**Standardize on React community convention: Remove `I` prefix** for component props interfaces.

**Files to Update**:
- `src/widgets/WWCCoPilot.tsx`: `IWWCCoPilotProps` → `WWCCoPilotProps`
- `src/widgets/MetaAnalysisView.tsx`: `IMetaAnalysisViewProps` → `MetaAnalysisViewProps`
- `src/widgets/ConflictView.tsx`: `IConflictViewProps` → `ConflictViewProps`
- `src/widgets/SynthesisWorkbench.tsx`: `ISynthesisWorkbenchProps` → `SynthesisWorkbenchProps`
- `src/widgets/PaperCard.tsx`: `IPaperCardProps` → `PaperCardProps`
- `src/widgets/DetailView.tsx`: `IDetailViewProps` → `DetailViewProps`

**Note**: Keep `I` prefix for data/API interfaces (`IWWCAssessment`, `IPaper`, etc.) as they represent data structures, not component props.

**Priority**: Low - Cosmetic, but improves consistency with React conventions

---

## 11. Percentage Formatting Utility

### Issue
Percentage formatting repeated in multiple places:
- `WWCCoPilot.tsx` (lines 183, 188): `(assessment.overall_attrition * 100).toFixed(1)}%`
- `ConflictView.tsx` (line 34): `(conflict.confidence * 100).toFixed(1)}%`
- `MetaAnalysisView.tsx` (line 34, 76): `(study.weight * 100).toFixed(1)}%`

### Recommendation
**Create formatting utility**:

```typescript
// src/utils/formatting.ts
export function formatPercentage(value: number, decimals: number = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

export function formatNumber(value: number, decimals: number = 3): string {
  return value.toFixed(decimals);
}
```

**Priority**: Low - Small duplication, but improves consistency

---

## 12. Header Component Pattern

### Issue
Header pattern with title and close button repeated:
- `WWCCoPilot.tsx` (lines 65-75)
- `SynthesisWorkbench.tsx` (lines 65-75)

### Recommendation
**Create a reusable `WidgetHeader` component**:

```typescript
// src/widgets/WidgetHeader.tsx
import React from 'react';
import { CloseButton } from './CloseButton';

interface IWidgetHeaderProps {
  title: string;
  onClose?: () => void;
  className?: string;
}

export const WidgetHeader: React.FC<IWidgetHeaderProps> = ({
  title,
  onClose,
  className = 'jp-jupyterlab-research-assistant-wwc-copilot-wwc-header'
}) => {
  return (
    <div className={className}>
      <h2>{title}</h2>
      {onClose && <CloseButton onClick={onClose} />}
    </div>
  );
};
```

**Priority**: Low - Small duplication

---

## 13. API Function Request Pattern

### Issue
All new API functions follow similar pattern but have slight variations in error messages and request body structure.

### Observation
The pattern is actually quite clean and consistent. The only improvement would be to ensure all use `handleAPIResponse` (see #9).

**Priority**: N/A - Already addressed in #9

---

## 14. CSS Class Naming Consistency

### Issue
All CSS classes follow the pattern `jp-jupyterlab-research-assistant-wwc-copilot-*`, which is good. However, some inconsistencies:
- Some use `-wwc-` in class names (`wwc-header`, `wwc-field`)
- Some use full feature names (`meta-analysis-summary`, `conflict-item`)

### Recommendation
**Standardize on feature-based naming** (already mostly done):
- `wwc-*` for WWC Co-Pilot specific styles
- `meta-analysis-*` for meta-analysis specific styles
- `conflict-*` for conflict detection specific styles
- `synthesis-*` for synthesis workbench specific styles

**Priority**: Low - Mostly consistent already

---

## 15. Type Safety Improvements

### Issue
Some `any` types used in `index.tsx`:
- Line 51: `let aiConfig: any = null;`
- Line 61: `const composite = settings.composite as any;`
- Line 202: `execute: (args: any) => {`
- Line 224: `execute: (args: any) => {`
- Line 319: `const path = (args as any).path as string;`
- Line 360: `const path = (args as any).path as string;`

### Recommendation
**Define proper types**:

```typescript
// src/types/settings.ts
export interface IAIConfig {
  enabled?: boolean;
  provider?: string;
  apiKey?: string;
  model?: string;
  ollamaUrl?: string;
}

export interface IPluginSettings {
  aiExtraction?: IAIConfig;
}

// src/types/commands.ts
export interface IOpenSynthesisArgs {
  paperIds?: number[];
}

export interface IOpenWWCArgs {
  paperId?: number;
  paperTitle?: string;
}

export interface IFileBrowserArgs {
  path?: string;
}
```

**Files to Update**:
- `src/index.tsx` (replace `any` types)

**Priority**: Medium - Improves type safety

---

## Implementation Priority Summary

### High Priority (Significant Impact)
1. **#3: Loading State Pattern** - Custom hook to reduce duplication
2. **#9: API Error Handling** - Use existing `handleAPIResponse` utility

### Medium Priority (Good Improvements)
3. **#1: Error Handling Inconsistency** - Standardize on `showError`
4. **#2: Custom Event Communication** - Type-safe event utility
5. **#6: Tab Component** - Reusable tab navigation
6. **#8: File Download Utility** - Prevent future duplication
7. **#15: Type Safety** - Remove `any` types

### Low Priority (Nice to Have)
8. **#4: Boolean Select Component** - Small duplication
9. **#5: Close Button Component** - Small duplication
10. **#7: Empty State Component** - Small duplication
11. **#10: Interface Naming** - Cosmetic consistency
12. **#11: Percentage Formatting** - Small duplication
13. **#12: Header Component** - Small duplication
14. **#14: CSS Naming** - Mostly consistent already

---

## Notes

- All refactorings are **non-breaking** - they improve internal structure without changing external APIs
- Can be implemented incrementally
- Should be done after Stage 2 is complete and tested
- Consider creating a separate refactoring branch to keep changes isolated
- Test thoroughly after each refactoring

---

## Files Changed Summary

**Frontend Files Modified/Created in Stage 2**:
- `src/api.ts` - Added 3 new API functions
- `src/index.tsx` - Added commands and event listeners
- `src/widgets/WWCCoPilot.tsx` - NEW
- `src/widgets/SynthesisWorkbench.tsx` - NEW
- `src/widgets/MetaAnalysisView.tsx` - NEW
- `src/widgets/ConflictView.tsx` - NEW
- `src/widgets/LibraryTab.tsx` - Added multi-select
- `src/widgets/PaperCard.tsx` - Added checkbox
- `src/widgets/DetailView.tsx` - Added WWC button
- `style/index.css` - Added styles for new components

**Total Lines Changed**: ~1,500+ lines of frontend code

